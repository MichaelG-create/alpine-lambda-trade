import json
import asyncio
import boto3
import logging
from typing import List
from src.producer.config import settings

logger = logging.getLogger(__name__)

class KinesisClient:
    def __init__(self):
        client_kwargs = {
            "region_name": settings.aws_region
        }
        if settings.aws_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_endpoint_url
        if settings.aws_access_key_id:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            
        self.kinesis_client = boto3.client('kinesis', **client_kwargs)
        self.stream_name = settings.kinesis_stream_name

    async def push_trades(self, trades: List[dict]):
        if not trades:
            return
        
        await asyncio.to_thread(self._put_records, trades)

    def _put_records(self, trades: List[dict]):
        records = []
        for trade in trades:
            partition_key = trade.get('symbol', 'unknown')
            data = json.dumps(trade).encode('utf-8')
            records.append({
                'Data': data,
                'PartitionKey': partition_key
            })
            
        for i in range(0, len(records), 500):
            chunk = records[i:i+500]
            try:
                self.kinesis_client.put_records(
                    Records=chunk,
                    StreamName=self.stream_name
                )
            except Exception as e:
                logger.error(f"Error pushing to kinesis: {e}")
