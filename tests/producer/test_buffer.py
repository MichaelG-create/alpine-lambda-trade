import pytest
from src.producer.s3_buffer import S3Buffer
from src.producer.config import settings

@pytest.mark.asyncio
async def test_s3_buffer_flush(s3_client):
    # s3_client is provided by moto mock fixture
    buffer = S3Buffer()
    
    trade = {
        "id": "1",
        "symbol": "BTC/USDT",
        "price": 50000.0,
        "amount": 1.0,
        "side": "buy",
        "timestamp": 1629811200000,
        "datetime": "2021-08-24T12:00:00.000Z"
    }
    
    settings.s3_dump_interval_seconds = 0
    await buffer.add_trade(trade)
    
    assert len(buffer.buffer) == 0
    
    bucket_objects = s3_client.list_objects_v2(Bucket=settings.s3_bucket_name)
    assert "Contents" in bucket_objects
    assert len(bucket_objects["Contents"]) == 1
    assert bucket_objects["Contents"][0]["Key"].startswith("ticker/")
