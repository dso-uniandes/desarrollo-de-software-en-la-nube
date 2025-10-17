import json
from  message_broker.client import producer as mb_producer

TASKS_CONFIG = {
    "topic": "video_tasks",
}

def dispatch_task(task_data: list[dict], topic: str) -> None:
    if topic not in TASKS_CONFIG.values():
        raise ValueError(f"Unknown topic: {topic}")
    
    for message in task_data:
        mb_producer.produce(topic, value=json.dumps(message).encode('utf-8'))
    mb_producer.flush()
    
    print(f"Dispatched {len(task_data)} tasks to topic '{topic}'")