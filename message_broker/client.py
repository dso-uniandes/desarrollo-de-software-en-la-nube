import os
import logging

from confluent_kafka import Producer
from utils.config import config

logger = logging.getLogger(__name__)

bootstrap_servers = config.KAFKA_BOOTSTRAP_SERVERS
if not bootstrap_servers:
    logger.error("❌ KAFKA_BOOTSTRAP_SERVERS not set. Kafka producer will not connect.")
else:
    logger.info(f"✅ Kafka producer configured with {bootstrap_servers}")

conf = {'bootstrap.servers': bootstrap_servers}


def get_producer() -> Producer | None:
    if config.ENV_STATE == 'test':
        return None
    try:
        return Producer(conf)
    except Exception as e:
        logger.error(f"❌ Error creating Kafka Producer: {e}")
        return None


producer = get_producer()
