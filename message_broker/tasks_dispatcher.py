import json
import logging

from message_broker.client import sqs

logger = logging.getLogger(__name__)

from utils.config import config

TASKS_CONFIG = {
    "topic": "video_tasks",
}


def dispatch_task(task_data: list[dict], topic: str) -> None:
    if config.ENV_STATE == 'test':
        logger.info("Test environment detected, skipping task dispatch.")
        return

    if sqs is None:
        logger.error("SQS client is not initialized. Cannot dispatch tasks.")
        return
    if topic not in TASKS_CONFIG.values():
        raise ValueError(f"Unknown topic: {topic}")

    for message in task_data:
        sqs.send_message(QueueUrl=config.VIDEO_QUEUE_URL, MessageBody=json.dumps(message), MessageGroupId=topic, MessageDeduplicationId=message["task_id"])

    logger.info(f"Dispatched {len(task_data)} tasks to topic '{topic}'")
