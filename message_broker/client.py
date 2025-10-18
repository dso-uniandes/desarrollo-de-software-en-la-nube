import os
from confluent_kafka import Producer
from utils.config import config

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

conf = {'bootstrap.servers': bootstrap_servers}

def get_producer() -> Producer:
    if config.ENV_STATE == 'test':
        return None
    return Producer(conf)

producer = get_producer()