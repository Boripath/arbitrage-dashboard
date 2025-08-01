# 📁 snapshot_runner.py
import pandas as pd
from fetch import fetch_deribit, fetch_binance, fetch_bybit
from utils.calculate_apy import calculate_apy
from storage.save_snapshot import save_snapshot
from storage.upload_to_gdrive import upload_to_gdrive
from datetime import datetime
import os

# ✅ Settings
ASSETS = ["BTC", "ETH"]
EXCHANGES = ["Deribit", "Binance", "Bybit"]  # You can modify this list
SAVE_TO_GDRIVE = True  # Set to False if you want to skip Google Drive upload
GDRIVE_FOLDER_ID = None  # Replace with your folder ID if needed

# ✅ Step 1: Fetch all data
all_data = []
fetch_map = {
    "Deribit": fetch_deribit,
    "Binance": fetch_binance,
    "Bybit": fetch_bybit,
}

for ex in EXCHANGES:
    try:
        df = fetch_map[ex](assets=ASSETS)
        df["Exchange"] = ex
        all_data.append(df)
        print(f"✅ Fetched from {ex}: {len(df)} rows")
    except Exception as e:
        print(f"❌ Failed to fetch from {ex}: {e}")

# ✅ Step 2: Combine and calculate APY
if all_data:
    df_all = pd.concat(all_data, ignore_index=True)
    df_result = calculate_apy(df_all)

    # ✅ Step 3: Save snapshot to local
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{timestamp}.parquet"
    local_path = save_snapshot(df_result, filename)

    # ✅ Step 4: Upload to Google Drive
    if SAVE_TO_GDRIVE:
        try:
            file_id = upload_to_gdrive(local_path, gdrive_folder_id=GDRIVE_FOLDER_ID)
        except Exception as e:
            print(f"⚠️ Google Drive upload failed: {e}")
else:
    print("⚠️ No data collected. Check API or settings.")
