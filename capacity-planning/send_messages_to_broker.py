#!/usr/bin/env python3
import argparse
import json
import logging
from dotenv import load_dotenv
import os
import uuid
import signal
import sys
import boto3

load_dotenv()
# ---------- CONFIG ----------
PROD_VIDEO_QUEUE_URL = os.getenv("PROD_VIDEO_QUEUE_URL")
S3_ACCESS_KEY_ID = os.getenv("PROD_S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("PROD_S3_SECRET_ACCESS_KEY")
S3_REGION = os.getenv("PROD_S3_REGION")

# Fixed list of sample video IDs
NORMAL_VIDEO_ID = 54
HEAVY_VIDEO_ID = 44  # example heavy video id

# Example user
DEFAULT_USER_ID = 1

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Graceful shutdown flag
stop_requested = False


# ---------- SIGNAL HANDLERS ----------
def handle_exit(signum, frame):
    global stop_requested
    stop_requested = True
    logger.warning(f"⚠️ Received signal {signum}. Stopping gracefully...")


signal.signal(signal.SIGINT, handle_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # kill

# ---------- PRODUCER ----------
sqs = None
def get_sqs():
    try:
        sqs = boto3.client(
            "sqs",
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
            region_name=S3_REGION,
        )
        return sqs
    except Exception as e:
        logger.error(f"❌ Error Connecting to SQS Queue: {e}")
        return None



# ---------- FUNCTIONS ----------
def dispatch_task(task_data: list[dict], topic: str) -> None:
    sqs = get_sqs()
    if sqs is None:
        logger.error("SQS client is not initialized. Cannot dispatch tasks.")
        return

    for message in task_data:
        sqs.send_message(QueueUrl=PROD_VIDEO_QUEUE_URL, MessageBody=json.dumps(message), MessageGroupId=topic, MessageDeduplicationId=message["task_id"])

    logger.info(f"Dispatched {len(task_data)} tasks to topic '{topic}'")

def generate_tasks(video_ids, user_id, count) -> list[dict]:
    """Generate tasks with random UUIDs for task_id."""
    tasks = []
    for _ in range(count):
        for video_id in video_ids:
            task_id = str(uuid.uuid4())
            task_info = {
                "video_id": video_id,
                "user_id": user_id,
                "task_id": task_id,
            }
            tasks.append(task_info)
    return tasks


# ---------- MAIN ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send video processing tasks to Kafka."
    )
    parser.add_argument(
        "--mode",
        choices=["normal", "heavy"],
        default="normal",
        help="Select mode: normal (all videos) or heavy (one heavy video).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of times to send each task.",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=DEFAULT_USER_ID,
        help="User ID to include in the message.",
    )

    args = parser.parse_args()

    # Choose which video IDs to use
    video_ids = [NORMAL_VIDEO_ID] if args.mode == "normal" else [HEAVY_VIDEO_ID]

    logger.info(f"Connecting to SQS at {PROD_VIDEO_QUEUE_URL}...")
    logger.info(f"Mode: {args.mode} | Count: {args.count} | User: {args.user_id}")

    try:
        sqs = get_sqs()
        task_list = generate_tasks(video_ids, args.user_id, args.count)
        dispatch_task(task_list, "video_tasks")
        logger.info("🚀 All messages successfully sent.")
        if sqs is None: 
            raise RuntimeError("SQS client is None after initialization.")
    except KeyboardInterrupt:
        logger.warning("⚠️ Interrupted by user (Ctrl+C). Flushing remaining messages...")
       
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error sending messages to SQS: {e}")
        sys.exit(1)