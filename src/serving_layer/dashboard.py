import streamlit as st
import snowflake.connector
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="ALT Real-Time Portfolio", layout="wide")

@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        database="ALT_DB",
        schema="STAGING" 
    )

sf = init_connection()

st.title("🚀 Alpine Lambda Trade (ALT) - Real-Time Portfolio")

@st.cache_data(ttl=5) # Real-Time caching every 5 seconds
def get_historical_data():
    cursor = sf.cursor()
    cursor.execute("""
    SELECT 
        TRADE_TIMESTAMP,
        SYMBOL,
        PRICE,
        SOURCE_LAYER,
        SPIKE_DETECTED,
        EMA
    FROM ALT_DB.STAGING_SERVING.VW_REALTIME_PORTFOLIO
    ORDER BY TRADE_TIMESTAMP DESC
    LIMIT 2000
    """)
    return cursor.fetch_pandas_all()

@st.cache_data(ttl=5)
def get_kpis():
    cursor = sf.cursor()
    query = """
    SELECT 
        COUNT(*) as TOTAL_TRADES,
        SUM(IFF(SPIKE_DETECTED = TRUE AND TRADE_TIMESTAMP >= DATEADD(HOUR, -1, CURRENT_TIMESTAMP()), 1, 0)) as RECENT_SPIKES
    FROM ALT_DB.STAGING_SERVING.VW_REALTIME_PORTFOLIO
    """
    cursor.execute(query)
    return cursor.fetch_pandas_all()

df = get_historical_data()
kpis_df = get_kpis()

# Header KPIs
total_trades = kpis_df['TOTAL_TRADES'].iloc[0] if not kpis_df.empty else 0
recent_spikes = kpis_df['RECENT_SPIKES'].iloc[0] if not kpis_df.empty else 0
# Gracefully handle NaN or None when counting spikes
recent_spikes = int(recent_spikes) if pd.notna(recent_spikes) else 0

if not df.empty:
    latest = df.iloc[0]
    current_price = latest['PRICE']
    current_ema = latest['EMA'] if pd.notna(latest['EMA']) else 0
else:
    current_price = 0
    current_ema = 0

diff = current_price - current_ema

col1, col2, col3 = st.columns(3)
col1.metric("📈 Total Trades Count (Historique + Live)", f"{total_trades:,}")
col2.metric("🎯 Current Price vs EMA", f"${current_price:,.2f}", f"{diff:,.2f} Delta" if diff != 0 else "0.00")
col3.metric("⚠️ Spike Alert Counter (Last 1H)", recent_spikes)

st.divider()

st.subheader("Price Movements & Volatility Anomalies")

if not df.empty:
    # Main line chart
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('TRADE_TIMESTAMP:T', title='Time'),
        y=alt.Y('PRICE:Q', scale=alt.Scale(zero=False), title='Market Price'),
        color=alt.Color('SYMBOL:N', title='Ticker')
    ).properties(height=400)

    # Spike Markers overlay
    spikes = df[df['SPIKE_DETECTED'] == True]
    if not spikes.empty:
        spike_chart = alt.Chart(spikes).mark_point(color='red', size=100, shape='square').encode(
            x='TRADE_TIMESTAMP:T',
            y='PRICE:Q',
            tooltip=['SYMBOL', 'PRICE', 'EMA', 'SOURCE_LAYER']
        )
        chart = chart + spike_chart

    st.altair_chart(chart, use_container_width=True)

st.subheader("Last 50 Ledger Transactions")
# Style dataframe to highlight the source
if not df.empty:
    st.dataframe(df.head(50), use_container_width=True)
