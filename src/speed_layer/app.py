import os
import json
import base64
import logging
import snowflake.connector

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Module-level cache for Warm invocations across batches
# Memory layout: { 'BTC/USDT': { 'ema': 50000.0, 'alpha': 0.1 } }
ema_cache = {}
THRESHOLD = 0.02 # 2% anomaly spike variation allowed

sf_conn = None

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        database='ALT_DB',
        schema='STAGING'
    )

def lambda_handler(event, context):
    global sf_conn
    
    if sf_conn is None or sf_conn.is_closed():
        logger.info("Initializing fresh Snowflake connection")
        sf_conn = get_snowflake_connection()

    records_to_insert = []
    
    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        try:
            trade = json.loads(payload)
        except Exception as e:
            logger.error(f"Failed parsing json Payload: {e}")
            continue
            
        symbol = trade.get('symbol')
        price = float(trade.get('price', 0))
        trade_id = trade.get('id')
        dt = trade.get('datetime')
        
        # EMA Core Mathematical Logic & Caching 
        if symbol not in ema_cache:
            ema_cache[symbol] = { 'ema': price, 'alpha': 0.1 }  # Initialize
        else:
            prev_ema = ema_cache[symbol]['ema']
            alpha = ema_cache[symbol]['alpha']
            # EMA_today = (Value_today * a) + (EMA_yesterday * (1 - a))
            new_ema = (price * alpha) + (prev_ema * (1 - alpha))
            ema_cache[symbol]['ema'] = new_ema
        
        current_ema = ema_cache[symbol]['ema']
        spike_detected = abs(price - current_ema) / current_ema > THRESHOLD

        records_to_insert.append((
            trade_id, symbol, price, current_ema, spike_detected, dt
        ))
        
    if records_to_insert:
        try:
            cursor = sf_conn.cursor()
            query = """
            INSERT INTO STG_REALTIME (TRADE_ID, SYMBOL, PRICE, EMA, SPIKE_DETECTED, TRADE_TIMESTAMP)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(query, records_to_insert)
            logger.info(f"Inserted {len(records_to_insert)} records into STG_REALTIME successfully.")
        except Exception as e:
            logger.error(f"Snowflake Insert Error: {e}")
            raise e

    return {
        'statusCode': 200,
        'body': f"Speed Layer logic processed {len(records_to_insert)} trades"
    }
