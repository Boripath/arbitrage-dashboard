import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from glob import glob
from scipy.stats import zscore

# ตั้งค่า UI
st.title("📊 Historical Arbitrage Snapshot Analyzer")
st.markdown("---")

# โหลด snapshot ทั้งหมดจาก data/snapshots/*.parquet
snapshot_files = sorted(glob("data/snapshots/*.parquet"))
if not snapshot_files:
    st.warning("❗ No snapshot files found in data/snapshots/")
    st.stop()

# ผู้ใช้เลือกไฟล์ snapshot
selected_file = st.selectbox("📁 Select a snapshot to analyze:", snapshot_files[::-1])
df = pd.read_parquet(selected_file)
st.success(f"✅ Loaded: {selected_file} ({len(df)} rows)")

# แสดง preview
df_preview = df.copy()
df_preview["timestamp"] = pd.to_datetime(df_preview["timestamp"])
st.dataframe(df_preview.head(20))

# เพิ่ม column ช่วยวิเคราะห์
if "spread_per_day" not in df.columns:
    df["spread_per_day"] = df["spread"] / df["days_to_expiry"].replace(0, 1)
if "zscore_spread_per_day" not in df.columns:
    df["zscore_spread_per_day"] = zscore(df["spread_per_day"].fillna(0))

# Filter โดย asset/exchange
assets = st.multiselect("🔍 Filter by asset:", df["asset"].unique().tolist(), default=df["asset"].unique().tolist())
exchanges = st.multiselect("🏦 Filter by exchange:", df["exchange"].unique().tolist(), default=df["exchange"].unique().tolist())
filtered_df = df[df["asset"].isin(assets) & df["exchange"].isin(exchanges)]

# Distribution plot ของ spread_per_day
st.subheader("📈 Spread per Day Distribution")
for asset in assets:
    fig, ax = plt.subplots()
    sns.histplot(filtered_df[filtered_df["asset"] == asset]["spread_per_day"], kde=True, bins=30, ax=ax)
    ax.set_title(f"Spread per Day Distribution: {asset}")
    st.pyplot(fig)

# Distribution plot ของ zscore
st.subheader("📉 Z-score of Spread per Day")
for asset in assets:
    fig, ax = plt.subplots()
    sns.histplot(filtered_df[filtered_df["asset"] == asset]["zscore_spread_per_day"], kde=True, bins=30, ax=ax)
    ax.set_title(f"Z-score of Spread per Day: {asset}")
    st.pyplot(fig)

# Top-N Z-score entries
st.subheader("🔝 Top Arbitrage Opportunities by Z-score")
top_n = st.slider("Select top N:", min_value=5, max_value=50, value=10)
st.dataframe(filtered_df.sort_values("zscore_spread_per_day", ascending=False).head(top_n))
