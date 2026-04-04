{{ config(materialized='view') }}

WITH historical AS (
    SELECT 
        trade_id,
        symbol,
        price,
        trade_timestamp,
        'BATCH' as source_layer,
        FALSE as spike_detected,
        NULL as ema
    FROM {{ ref('slv_trades') }}
),

real_time AS (
    SELECT 
        trade_id,
        symbol,
        price,
        trade_timestamp,
        'SPEED' as source_layer,
        -- Need to explicitly cast to BOOLEAN to prevent union conflicts or Variant parsing
        CAST(spike_detected AS BOOLEAN) as spike_detected,
        CAST(ema AS FLOAT) as ema
    FROM {{ source('alpine_lambda_trade_source', 'STG_REALTIME') }}
    -- Filter out overlaps seamlessly
    WHERE trade_timestamp > (SELECT MAX(trade_timestamp) FROM historical)
)

SELECT * FROM historical
UNION ALL
SELECT * FROM real_time
