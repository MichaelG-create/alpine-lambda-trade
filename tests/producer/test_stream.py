import pytest
import json
from src.producer.kinesis_client import KinesisClient
from src.producer.config import settings

@pytest.mark.asyncio
async def test_kinesis_push(kinesis_client):
    client = KinesisClient()
    
    trade = {
        "id": "1",
        "symbol": "BTC/USDT",
        "price": 50000.0,
        "amount": 1.0,
        "side": "buy",
        "timestamp": 1629811200000,
        "datetime": "2021-08-24T12:00:00.000Z"
    }
    
    await client.push_trades([trade])
    
    stream_info = kinesis_client.describe_stream(StreamName=settings.kinesis_stream_name)
    shard_id = stream_info['StreamDescription']['Shards'][0]['ShardId']
    
    iterator_resp = kinesis_client.get_shard_iterator(
        StreamName=settings.kinesis_stream_name,
        ShardId=shard_id,
        ShardIteratorType='TRIM_HORIZON'
    )
    
    records_resp = kinesis_client.get_records(ShardIterator=iterator_resp['ShardIterator'])
    assert len(records_resp['Records']) == 1
    
    record_data = json.loads(records_resp['Records'][0]['Data'].decode('utf-8'))
    assert record_data['id'] == "1"
    assert record_data['symbol'] == "BTC/USDT"
    assert records_resp['Records'][0]['PartitionKey'] == "BTC/USDT"
