import pytest
import json
from src.producer.sqs_client import SQSClient
from src.producer.config import settings

@pytest.mark.asyncio
async def test_sqs_push(sqs_client):
    client = SQSClient()
    
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
    
    # Verify the message was pushed to SQS
    response = sqs_client.get_queue_url(QueueName='alt-ticker-queue')
    queue_url = response['QueueUrl']
    
    messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
    assert 'Messages' in messages
    assert len(messages['Messages']) == 1
    
    record_data = json.loads(messages['Messages'][0]['Body'])
    assert record_data['id'] == "1"
    assert record_data['symbol'] == "BTC/USDT"
