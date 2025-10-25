import os
from confluent_kafka import Producer
from utils.config import config

bootstrap_servers = config.KAFKA_BOOTSTRAP_SERVERS

conf = {'bootstrap.servers': bootstrap_servers}

def get_producer() -> Producer:
    if config.ENV_STATE == 'test':
        return None
    return Producer(conf)

producer = get_producer()