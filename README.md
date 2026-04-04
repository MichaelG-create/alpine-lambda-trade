# Alpine Lambda Trade (ALT)

## Architecture

This project implements a Lambda Architecture (Batch + Speed Layers) for a real-time Crypto analytics platform connecting AWS and Snowflake.

```mermaid
graph TD
    WS((Crypto WebSocket))
    
    subgraph "Producer Layer"
        P[CCXT Python Producer]
    end
    
    subgraph "Speed Layer (Real-time)"
        Kinesis[AWS Kinesis Stream<br>alt-ticker-stream]
        Lambda[AWS Lambda<br>EMA Calculation / Alerts]
    end
    
    subgraph "Batch Layer (Historical)"
        S3[AWS S3 Bucket<br>alt-raw-data]
        Snowpipe[Snowpipe<br>Auto-ingest]
        dbt[dbt<br>Silver/Gold Models]
    end
    
    subgraph "Serving Layer"
        STG_REAL_TIME[(Snowflake<br>STG_REALTIME)]
        BATCH_DB[(Snowflake<br>Historical Tables)]
        View[VW_REALTIME_PORTFOLIO]
    end
    
    WS --> P
    P -->|Stream trades| Kinesis
    P -->|Batch Parquet (5m)| S3
    
    Kinesis --> Lambda
    Lambda --> STG_REAL_TIME
    
    S3 --> Snowpipe
    Snowpipe --> BATCH_DB
    BATCH_DB --> dbt
    
    STG_REAL_TIME --> View
    dbt --> View
```

## Business Problems & Solutions

### P1: Le Risque de "Slippage" (Volatilité)
- **Problème :** Un décalage de prix de 2% en 60s peut ruiner une stratégie de trading. C'est inacceptable en Crypto.
- **Solution ALT :** Speed Layer (Kinesis + Lambda) calculant une EMA en temps réel pour déclencher une alerte visuelle/système en < 1s.

### P2: L'Auditabilité et la Stratégie (Historique)
- **Problème :** Impossible de backtester une stratégie ou de prouver la conformité sans une donnée "propre" et immuable.
- **Solution ALT :** Batch Layer (S3 + dbt) garantissant une "Source of Truth" dédoublonnée, typée et archivée pour des analyses de corrélation sur 6 mois.

### P3: La Valorisation "Live" du Portefeuille (P&L)
- **Problème :** Les gestionnaires voient souvent leur P&L avec 15min de retard. C'est inacceptable en Crypto.
- **Solution ALT :** Serving Layer (Unified View) fusionnant les positions historiques et le dernier prix du marché pour un P&L "Up-to-the-millisecond".
