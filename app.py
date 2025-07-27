import streamlit as st
import pandas as pd
from fetch import fetch_deribit, fetch_binance, fetch_bybit
from utils.calculate_apy import calculate_apy_and_zscore
from datetime import datetime
import os

# Title
st.title("📊 Crypto Arbitrage Dashboard: BTC & ETH")
st.markdown("---")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
assets = st.sidebar.multiselect("Select Assets", ["BTC", "ETH"], default=["BTC", "ETH"])
show_apy_type = st.sidebar.radio("APY Display", ["Daily", "Annualized", "Both"], index=2)

# Fetch data
st.subheader("🔄 Fetching Price Data")
st.write("This may take a few seconds...")

# Fetch prices from all 3 exchanges
data_frames = []
for source_name, fetch_fn in zip([
    "Deribit", "Binance", "Bybit"
], [
    fetch_deribit.fetch_data,
    fetch_binance.fetch_data,
    fetch_bybit.fetch_data
]):
    try:
        df = fetch_fn(assets=assets)
        df['source'] = source_name
        data_frames.append(df)
        st.success(f"✅ {source_name} fetched: {len(df)} rows")
    except Exception as e:
        st.error(f"❌ {source_name} failed: {e}")

# Merge all data
if data_frames:
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Calculate APY + Z-score
    result_df = calculate_apy_and_zscore(combined_df)

    # Filter columns for display
    columns = ["source", "asset", "type", "expiry", "price", "spot_price", "spread", "days_to_expiry", "apy_daily", "apy_annual", "zscore"]
    result_df = result_df[columns]

    # Sort by zscore descending
    result_df = result_df.sort_values(by="zscore", ascending=False)

    # Display table
    st.subheader("📈 Arbitrage Opportunities")
    if show_apy_type == "Daily":
        st.dataframe(result_df[["source", "asset", "type", "expiry", "spread", "apy_daily", "zscore"]])
    elif show_apy_type == "Annualized":
        st.dataframe(result_df[["source", "asset", "type", "expiry", "spread", "apy_annual", "zscore"]])
    else:
        st.dataframe(result_df[["source", "asset", "type", "expiry", "spread", "apy_daily", "apy_annual", "zscore"]])

    # Export CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"data/arbitrage_{timestamp}.csv"
    result_df.to_csv(csv_path, index=False)
    st.success(f"📁 Saved data to: {csv_path}")
else:
    st.warning("⚠️ No data available. Please check your connection or API access.")

