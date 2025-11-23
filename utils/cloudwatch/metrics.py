import os
import logging
import boto3
from botocore.config import Config
from utils.config import config
from typing import Protocol, Any, Dict, runtime_checkable, cast

logger = logging.getLogger(__name__)


@runtime_checkable
class CloudWatch(Protocol):
    def put_metric_data(
        self, Namespace: str, MetricData: list[Dict[str, Any]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Put metric data to the specified CloudWatch namespace. Accepts extra boto3 params."""
        ...
    


def get_cloudwatch_client() -> CloudWatch | None:
    if config.ENV_STATE == "test":
        return None
    try:
        cloudwatch = boto3.client(
            "cloudwatch",
            aws_access_key_id=config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
            region_name=config.S3_REGION,
            config=Config(
                connect_timeout=5,
                read_timeout=5,
                retries={'max_attempts': 1}
            )
        )
        return cast(CloudWatch, cloudwatch)
    except Exception as e:
        logger.error(f"❌ Error Connecting to CloudWatch Queue: {e}")
        return None


cloudwatch = get_cloudwatch_client()

def publish_metrics(
    task_id: str,
    total_duration: float,
    db_fetch_duration: float | None,
    s3_download_duration: float | None,
    video_processing_duration: float | None,
    db_update_duration: float | None,
    success: bool,
    failure_stage: str | None
):
    """
    Publish detailed metrics to CloudWatch for observability.
    Each metric is independent, allowing filtered dashboards, alarms, and percentile analysis.
    """
    if not cloudwatch:
        logger.warning("CloudWatch client is not initialized. Skipping metric publishing.")
        return

    metric_data = []

    # ---- Helper to append metrics safely ----
    def add_metric(name: str, value: float | None, unit: str = "Seconds"):
        if value is not None:
            metric_data.append({
                "MetricName": name,
                "Value": value,
                "Unit": unit,
                "StorageResolution": 1,
                "Dimensions": [
                    {"Name": "Environment", "Value": config.ENV_STATE},
                    {"Name": "FailureStage", "Value": failure_stage or "NONE"},
                ],
            })

    # ----- Duration Metrics -----
    add_metric("TaskTotalTime", total_duration)
    add_metric("DBFetchTime", db_fetch_duration)
    add_metric("S3DownloadTime", s3_download_duration)
    add_metric("FFmpegProcessingTime", video_processing_duration)
    add_metric("DBUpdateTime", db_update_duration)

    # ----- Success / Failure Counters -----
    metric_data.append({
        "MetricName": "TaskSuccess",
        "Value": 1 if success else 0,
        "Unit": "Count",
        "Dimensions": [
            {"Name": "Environment", "Value": config.ENV_STATE},
            {"Name": "FailureStage", "Value": failure_stage or "NONE"},
        ],
    })

    metric_data.append({
        "MetricName": "TaskFailure",
        "Value": 0 if success else 1,
        "Unit": "Count",
        "Dimensions": [
            {"Name": "Environment", "Value": config.ENV_STATE},
            {"Name": "FailureStage", "Value": failure_stage or "NONE"},
        ],
    })

    # Final send with timeout (using existing client)
    try:
        cloudwatch.put_metric_data(
            Namespace="VideoWorker",
            MetricData=metric_data
        )
        print(f"📈 CloudWatch metrics published for task_id={task_id} (success={success})")

    except Exception as e:
        # You don't want metric publishing to break your workflow
        print(f"⚠️ Failed to push metrics for task_id={task_id}: {e}")
    if not cloudwatch:
        logger.warning("CloudWatch client is not initialized. Skipping metric publishing.")
        return