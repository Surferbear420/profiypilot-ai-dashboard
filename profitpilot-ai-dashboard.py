import streamlit as st
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockBarsRequest
from datetime import datetime, timedelta
import pandas as pd

# Local hardcoded keys for testing (regenerate after for security)
API_KEY = "PKKHATJX5SDO7MQSC36XOJUPJT"
SECRET_KEY = "59MsXuXvS9D59HpCJcqGrSkGNKGJPyu9GnZCC8FCzepf"

SYMBOLS = ["AAPL", "TSLA"]
THRESHOLD = 0.01
QUANTITY = 1

@st.cache_resource
def get_clients():
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    return trading_client, data_client

st.set_page_config(layout="wide")
st.title("🛡️ ProfitPilot AI Dashboard")
st.subheader("Autonomous Trading Bot (Paper Mode)")

st.sidebar.header("Bot Controls")
ENABLE_TRADING = st.sidebar.checkbox("Enable Paper Trades", value=False)
SYMBOL = st.sidebar.selectbox("Scan Symbol", SYMBOLS)

client, hist_client = get_clients()
try:
    account = client.get_account()
    positions = client.get_all_positions()
    st.success("✅ Connected to Alpaca! Account loaded.")
except Exception as e:
    st.error(f"❌ Alpaca Error: {e}")
    st.stop()

# Account Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Status", "Active")
with col2:
    st.metric("Total Balance", f"\${float(account.equity):,.2f}")
with col3:
    st.metric("Buying Power", f"\${float(account.buying_power):,.2f}")
with col4:
    st.metric("Cash", f"\${float(account.cash):,.2f}")

open_pl = 0
if positions:
    open_pl = sum(float(p.unrealized_pl) for p in positions)
st.metric("Open P&L", f"\${open_pl:,.2f}")
st.metric("Open Positions", len(positions))

# AI Scanner
st.subheader("🤖 AI Scanner")
end = datetime.now()
start = end - timedelta(days=1)
request = StockBarsRequest(symbol_or_symbols=SYMBOL, timeframe=TimeFrame(5, TimeFrameUnit.Minute), start=start, end=end)
bars = hist_client.get_stock_bars(request)

if not bars.df.empty:
    df = bars.df