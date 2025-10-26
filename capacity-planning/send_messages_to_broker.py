#!/usr/bin/env python3
import argparse
import json
import logging
import os
import uuid
import signal
import sys
from confluent_kafka import Producer

# ---------- CONFIG ----------
PROD_KAFKA_BOOTSTRAP_SERVERS = os.getenv("PROD_KAFKA_BOOTSTRAP_SERVERS", None)
TOPIC = "video_tasks"

# Fixed list of sample video IDs
NORMAL_VIDEO_ID = [101]
HEAVY_VIDEO_ID = 999  # example heavy video id

# Example user
DEFAULT_USER_ID = 9999

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
producer_conf = {"bootstrap.servers": PROD_KAFKA_BOOTSTRAP_SERVERS}

def get_producer() -> Producer:
    p = Producer(producer_conf)
    try:
        # wait up to 2 seconds for broker metadata (acts as a connect timeout)
        metadata = p.list_topics(timeout=2.0)
    except Exception as e:
        raise TimeoutError(f"Timed out connecting to Kafka brokers after 2s: {e}")
    if not getattr(metadata, "brokers", None) or len(metadata.brokers) == 0:
        raise TimeoutError("No Kafka brokers available after 2s")
    return p

producer = None

# ---------- FUNCTIONS ----------
def dispatch_task(task_data: list[dict], topic: str) -> None:
    """Send a list of task dicts to the given Kafka topic."""
    if producer is None:
        raise RuntimeError("Producer is not initialized.")
    
    for message in task_data:
        producer.produce(topic, value=json.dumps(message).encode("utf-8"))
    producer.flush()
    logger.info(f"✅ Dispatched {len(task_data)} tasks to topic '{topic}'")


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

    logger.info(f"Connecting to Kafka at {PROD_KAFKA_BOOTSTRAP_SERVERS}...")
    logger.info(f"Mode: {args.mode} | Count: {args.count} | User: {args.user_id}")

    try:
        producer = get_producer()
        task_list = generate_tasks(video_ids, args.user_id, args.count)
        dispatch_task(task_list, TOPIC)
        logger.info("🚀 All messages successfully sent.")
        if producer is None: 
            raise RuntimeError("Producer is None after initialization.")
    except KeyboardInterrupt:
        logger.warning("⚠️ Interrupted by user (Ctrl+C). Flushing remaining messages...")
        if producer is not None:
            producer.flush()
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error sending messages to Kafka: {e}")
        sys.exit(1)
    finally:
        if producer is not None:
            producer.flush()
        logger.info("🧹 Kafka producer closed gracefully.")