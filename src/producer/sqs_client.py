import boto3
import json
import uuid
import logging
from typing import List

logger = logging.getLogger(__name__)

class SQSClient:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        try:
            # We fetch the QueueUrl dynamically from its name
            response = self.sqs.get_queue_url(QueueName='alt-ticker-queue')
            self.queue_url = response['QueueUrl']
            logger.info(f"SQS Queue URL initialized: {self.queue_url}")
        except Exception as e:
            logger.warning(f"Could not get queue URL. Ensure 'alt-ticker-queue' exists. Details: {e}")
            self.queue_url = None

    async def push_trades(self, trades: List[dict]):
        if not self.queue_url or not trades:
            return
            
        entries = []
        for trade in trades:
            entries.append({
                'Id': str(uuid.uuid4()),
                'MessageBody': json.dumps(trade)
            })
            
        try:
            # boto3 is synchronous, we run it directly here since it's fast enough for SQS
            # send_message_batch takes maximum 10 items
            response = self.sqs.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            
            if 'Failed' in response:
                logger.error(f"Failed to push some trades to SQS: {response['Failed']}")
                
        except Exception as e:
            logger.error(f"Error pushing to SQS: {e}")
            raise e
