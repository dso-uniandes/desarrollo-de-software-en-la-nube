import os
from confluent_kafka import Consumer, KafkaException

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
group_id = os.getenv("KAFKA_GROUP_ID", "video_tasks_group")

conf = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

def process_video_processing(message: str):
    print(f"Processing video: {message}")
    # Here you would add the actual video processing logic
    # For example, using ffmpeg to transcode the video
    
def consume_messages(topic: str):
    consumer.subscribe([topic])
    try:
        while True:
            msg = consumer.poll(1.0)  # Timeout of 1 second
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            print(f"Received message: {msg.value().decode('utf-8')}")
            
            process_video_processing(msg.value().decode('utf-8'))

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()