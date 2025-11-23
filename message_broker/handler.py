import asyncio
import json
import logging

from message_broker.worker import process_video_processing
from storeapi.database import database
from utils.logging_conf import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger("LambdaHandler")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler function for processing SQS messages.
    
    Args:
        event: Lambda event containing SQS records
        context: Lambda context object
        
    Returns:
        dict: Response with status and processed messages count
    """
    
    logger.info(f"Lambda function invoked with event: {event}")
    
    try:
        # Initialize database connection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process_lambda_messages():
            await database.connect()
            logger.info("Database connection established.")
            
            processed_count = 0
            
            # Process SQS records from Lambda event
            if 'Records' in event:
                for record in event['Records']:
                    if record.get('eventSource') == 'aws:sqs':
                        try:
                            # Extract message body from SQS record
                            message_body = record['body']
                            logger.info(f"📩 Received SQS message body: {message_body}")
                            
                            # Parse the JSON message body
                            decoded_message = json.loads(message_body)
                            logger.info(f"🔍 Decoded message: {decoded_message}")
                            
                            # Process the video processing task
                            await process_video_processing(decoded_message)
                            processed_count += 1
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON from message body: {message_body}, error: {e}")
                        except KeyError as e:
                            logger.error(f"Missing required field in SQS record: {e}")
                        except Exception as e:
                            logger.error(f"Error processing SQS record: {e}")
                        
            await database.disconnect()
            return processed_count
        
        processed_count = loop.run_until_complete(process_lambda_messages())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {processed_count} messages',
                'processed_count': processed_count
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Error processing messages'
            })
        }
    finally:
        loop.close()

