import os
import logging
import boto3
from utils.config import config
from typing import Protocol, Any, Dict, runtime_checkable, cast

logger = logging.getLogger(__name__)


@runtime_checkable
class SQS(Protocol):
    def send_message(self, QueueUrl: str, MessageBody: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a message to the specified SQS queue. Accepts extra boto3 params (MessageGroupId, DelaySeconds, etc)."""
        ...
    def receive_message(self, QueueUrl: str, **kwargs: Any) -> Dict[str, Any]:
        """Receive messages from the specified SQS queue. Accepts extra boto3 params (MaxNumberOfMessages, WaitTimeSeconds, etc)."""
        ...
    def delete_message(self, QueueUrl: str, ReceiptHandle: str) -> Dict[str, Any]:
        """Delete a message from the specified SQS queue using its ReceiptHandle."""
        ...

def get_sqs_client() -> SQS | None:
    if config.ENV_STATE == 'test':
        return None
    try:
        sqs = boto3.client("sqs", region_name="us-east-2")
        return cast(SQS, sqs)
    except Exception as e:
        logger.error(f"❌ Error Connecting to SQS Queue: {e}")
        return None


sqs = get_sqs_client()
