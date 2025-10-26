#!/usr/bin/env python3

"""
Kafka producer for worker capacity tests.

Enqueues tasks into the 'video_tasks' topic to bypass the web/API layer.

Usage examples:
  python worker_load_producer.py \
    --bootstrap "localhost:9092" \
    --video-ids 12,34 \
    --count 200 \
    --rate 50

  python worker_load_producer.py \
    --bootstrap "localhost:9092" \
    --video-ids-file seed_output.json \
    --count 100 \
    --rate 0   # firehose (no delay)

Notes:
  - If multiple video IDs are provided, they will be cycled while enqueuing.
  - --rate is the approximate messages per second (best-effort sleep pacing).
"""

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import List

from confluent_kafka import Producer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enqueue tasks to Kafka for worker load tests")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", default="video_tasks", help="Kafka topic name")
    parser.add_argument("--video-ids", default="", help="Comma-separated list of video IDs to cycle through")
    parser.add_argument("--video-ids-file", default="", help="Path to JSON file with {'video_ids': [..]} format")
    parser.add_argument("--count", type=int, default=100, help="Total number of messages to enqueue")
    parser.add_argument("--rate", type=float, default=0.0, help="Approx messages per second (0 for max speed)")
    return parser.parse_args()


def load_video_ids(args: argparse.Namespace) -> List[int]:
    if args.video_ids:
        return [int(x.strip()) for x in args.video_ids.split(",") if x.strip()]
    if args.video_ids_file:
        p = Path(args.video_ids_file)
        if not p.exists():
            raise FileNotFoundError(f"video-ids file not found: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        vids = data.get("video_ids", [])
        return [int(x) for x in vids]
    raise ValueError("You must provide --video-ids or --video-ids-file")


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for {msg.key()}: {err}")
    # else:  # Avoid noisy output on success
    #     print(f"✅ Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def main():
    args = parse_args()
    video_ids = load_video_ids(args)
    if not video_ids:
        raise ValueError("No video IDs provided")

    producer = Producer({"bootstrap.servers": args.bootstrap})

    print(f"🚀 Enqueuing {args.count} tasks to '{args.topic}' @ {args.bootstrap}")
    print(f"🎯 Cycling video IDs: {video_ids}")
    if args.rate and args.rate > 0:
        print(f"⏱️  Rate limit: ~{args.rate} msg/s")
    else:
        print("💨 Firehose mode (no delay)")

    delay = 1.0 / args.rate if args.rate and args.rate > 0 else 0.0

    for i in range(args.count):
        video_id = video_ids[i % len(video_ids)]
        task_id = str(uuid.uuid4())
        payload = {"video_id": video_id, "task_id": task_id}
        producer.produce(args.topic, json.dumps(payload).encode("utf-8"), callback=delivery_report)

        if delay > 0:
            time.sleep(delay)

        if (i + 1) % 50 == 0:
            print(f"… enqueued {i + 1}/{args.count}")

    producer.flush()
    print("✅ All tasks enqueued!")


if __name__ == "__main__":
    main()


