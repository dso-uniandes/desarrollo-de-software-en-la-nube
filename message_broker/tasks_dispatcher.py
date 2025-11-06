import json
import logging

from message_broker.client import producer as mb_producer

logger = logging.getLogger(__name__)

from utils.config import config

TASKS_CONFIG = {
    "topic": "video_tasks",
}


def dispatch_task(task_data: list[dict], topic: str) -> None:
    if config.ENV_STATE == 'test':
        logger.info("Test environment detected, skipping task dispatch.")
        return

    if topic not in TASKS_CONFIG.values():
        raise ValueError(f"Unknown topic: {topic}")

    for message in task_data:
        mb_producer.produce(topic, value=json.dumps(message).encode('utf-8'))
    mb_producer.flush()

    logger.info(f"Dispatched {len(task_data)} tasks to topic '{topic}'")

    # try:
    #     for message in task_data:
    #         mb_producer.produce(topic, value=json.dumps(message).encode('utf-8'))
    #     mb_producer.flush(timeout=10)
    #     logger.info(f"Dispatched {len(task_data)} tasks to topic '{topic}'")
    # except Exception as e:
    #     logger.warning(f"Failed to dispatch tasks to Kafka: {e}. Continuing without task dispatch.")
