#!/usr/bin/env python3

"""
Seed test videos (files + DB rows) for worker capacity tests.

This script:
  - Generates or copies local files to the configured storage base (uploaded folder)
  - Creates DB rows in the 'videos' table with status='uploaded'
  - Prints a JSON with the created video IDs for use by the Kafka producer

Usage examples:
  python seed_videos.py --sizes 50,100 --base-name captest --user-id 1 --count-per-size 2

  python seed_videos.py --files /path/to/50mb.mp4,/path/to/100mb.mp4 --user-id 1

Notes:
  - By default, it will synthesize files of approximate size using 'dd' if no --files are provided.
  - Requires app config/env (.env loaded by utils.config) to connect DB and know storage paths.
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import asyncio
from utils.config import config
from utils.nfs.s3_local import s3_upload_video
from storeapi.database import database, video_table


def parse_args():
    parser = argparse.ArgumentParser(description="Seed test videos for worker load tests")
    parser.add_argument("--user-id", type=int, required=True, help="User ID owner for videos")
    parser.add_argument(
        "--sizes",
        default="50,100",
        help="Comma-separated sizes in MB to generate (ignored if --files provided)",
    )
    parser.add_argument(
        "--count-per-size", type=int, default=1, help="How many videos per size to create"
    )
    parser.add_argument(
        "--base-name", default="captest", help="Base name for generated video object keys"
    )
    parser.add_argument(
        "--files",
        default="",
        help="Comma-separated absolute file paths to use instead of generating (must match sizes length if provided)",
    )
    return parser.parse_args()


def synthesize_file(target_path: Path, size_mb: int) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Create approximate size file filled with zeros (fast, not a real video but good for IO/throughput tests)
    # If you need real mp4 content, replace with an ffmpeg command to transcode a sample and pad duration.
    block_size = 1_048_576  # 1MB
    count = size_mb
    subprocess.run(["dd", "if=/dev/zero", f"of={target_path}", f"bs={block_size}", f"count={count}", "status=none"], check=True)


async def insert_video_row(user_id: int, title: str, original_url: str) -> int:
    await database.connect()
    try:
        values = {
            "user_id": user_id,
            "title": title,
            "original_url": original_url,
            "processed_url": None,
            "status": "uploaded",
            "uploaded_at": datetime.now(),
            "processed_at": None,
        }
        query = video_table.insert().values(**values)
        video_id = await database.execute(query)
        return int(video_id)
    finally:
        await database.disconnect()


def main():
    args = parse_args()

    provided_files: List[str] = [p for p in args.files.split(",") if p.strip()]
    sizes_mb: List[int] = [int(x) for x in args.sizes.split(",") if x.strip()]

    created: List[Tuple[int, str]] = []  # (video_id, object_key)

    if provided_files:
        if len(provided_files) == 0:
            raise ValueError("--files provided but empty")
        # Use provided files as-is; upload to storage and create DB rows
        for idx, file_path in enumerate(provided_files, 1):
            src = Path(file_path)
            if not src.exists():
                raise FileNotFoundError(f"File not found: {src}")
            object_key = f"{config.UPLOADED_FOLDER}/seed_{args.base_name}_{idx}.mp4"
            url = s3_upload_video(str(src), object_key)
            title = f"{args.base_name}-{idx}"
            video_id = asyncio.run(insert_video_row(args.user_id, title, url))
            created.append((video_id, object_key))
    else:
        # Generate files of requested sizes
        for size in sizes_mb:
            for c in range(1, args.count_per_size + 1):
                object_key = f"{config.UPLOADED_FOLDER}/seed_{args.base_name}_{size}mb_{c}.mp4"
                tmp_src = Path(f"./tmp_seed_{size}mb_{c}.bin")
                synthesize_file(tmp_src, size)
                url = s3_upload_video(str(tmp_src), object_key)
                tmp_src.unlink(missing_ok=True)
                title = f"{args.base_name}-{size}mb-{c}"
                video_id = asyncio.run(insert_video_row(args.user_id, title, url))
                created.append((video_id, object_key))

    # Output JSON for chaining
    out = {
        "video_ids": [vid for vid, _ in created],
        "objects": [obj for _, obj in created],
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()


