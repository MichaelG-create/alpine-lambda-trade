import asyncio
import logging
import signal
import sys
from src.producer.config import settings
from src.producer.s3_buffer import S3Buffer
from src.producer.sqs_client import SQSClient
from src.producer.exchange_stream import ExchangeStream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing Producer services...")
    s3_buffer = S3Buffer()
    sqs_client = SQSClient()
    
    sqs_trade_buffer = []
    
    async def handle_trade(trade: dict):
        await s3_buffer.add_trade(trade)
        
        # Buffer for SQS batching (up to 10 max per batch)
        sqs_trade_buffer.append(trade)
        if len(sqs_trade_buffer) >= 10:
            batch_to_send = sqs_trade_buffer.copy()
            sqs_trade_buffer.clear()
            try:
                await sqs_client.push_trades(batch_to_send)
                logger.info(f"Pushed batch of {len(batch_to_send)} trades to SQS.")
            except Exception as e:
                logger.error(f"Failed to push trades to SQS: {e}")

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
        
        if len(sqs_trade_buffer) > 0:
            logger.info(f"Flushing remaining {len(sqs_trade_buffer)} trades to SQS...")
            try:
                await sqs_client.push_trades(sqs_trade_buffer)
            except Exception as e:
                pass

        logger.info("Shutdown complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
