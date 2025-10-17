import os
from confluent_kafka import Producer

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

conf = {'bootstrap.servers': bootstrap_servers}
producer = Producer(conf)
