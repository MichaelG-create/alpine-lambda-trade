import io
import time
import pandas as pd
import asyncio
import boto3
from datetime import datetime, timezone
from src.producer.config import settings

class S3Buffer:
    def __init__(self):
        self.buffer = []
        self.last_dump_time = time.time()
        
        client_kwargs = {
            "region_name": settings.aws_region
        }
        if settings.aws_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_endpoint_url
        if settings.aws_access_key_id:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            
        self.s3_client = boto3.client('s3', **client_kwargs)

    async def add_trade(self, trade_dict: dict):
        self.buffer.append(trade_dict)
        now = time.time()
        
        if now - self.last_dump_time >= settings.s3_dump_interval_seconds:
            await self.flush()

    async def flush(self):
        if not self.buffer:
            self.last_dump_time = time.time()
            return
        
        trades_to_dump = self.buffer
        self.buffer = []
        self.last_dump_time = time.time()
        
        await asyncio.to_thread(self._upload_to_s3, trades_to_dump)
        print(f"Flushed {len(trades_to_dump)} trades to S3.")

    def _upload_to_s3(self, trades: list[dict]):
        df = pd.DataFrame(trades)
        
        now = datetime.now(timezone.utc)
        path = f"ticker/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}/trades_{int(now.timestamp())}.parquet"
        
        buffer = io.BytesIO()
        df.to_parquet(buffer, engine="pyarrow", compression="snappy")
        
        try:
            self.s3_client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=path,
                Body=buffer.getvalue()
            )
        except Exception as e:
            print(f"Error uploading to S3: {e}")
