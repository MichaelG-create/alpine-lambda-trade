import asyncio
import logging
import signal
import sys
from src.producer.config import settings
from src.producer.s3_buffer import S3Buffer
from src.producer.kinesis_client import KinesisClient
from src.producer.exchange_stream import ExchangeStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing Producer services...")
    s3_buffer = S3Buffer()
    kinesis_client = KinesisClient()
    
    async def handle_trade(trade: dict):
        await s3_buffer.add_trade(trade)
        await kinesis_client.push_trades([trade])

    exchange_stream = ExchangeStream(callbacks=[handle_trade])
    
    def shutdown_signal():
        logger.info("Shutdown signal received")
        asyncio.create_task(exchange_stream.stop())
        
    loop = asyncio.get_event_loop()
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown_signal)
    
    try:
        await exchange_stream.start()
    finally:
        logger.info("Flushing remaining buffer to S3...")
        await s3_buffer.flush()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
