# snapshot_runner.py

import pandas as pd
from datetime import datetime
from fetch.fetch_deribit import fetch_deribit
from fetch.fetch_binance import fetch_binance
from fetch.fetch_bybit import fetch_bybit
from utils.calculate_apy import calculate_apy
from storage.save_snapshot import save_snapshot
from storage.upload_to_gdrive import upload_to_gdrive

# ตั้งค่าเริ่มต้น
ASSETS = ["BTC", "ETH"]
EXCHANGES = {
    "Deribit": fetch_deribit,
    "Binance": fetch_binance,
    "Bybit": fetch_bybit,
}
ENABLED_EXCHANGES = ["Deribit"]  # ✅ ดึงจาก Deribit เท่านั้นในเวอร์ชันแรก

def main():
    print("📡 Starting snapshot fetch...")
    data_frames = []

    for name in ENABLED_EXCHANGES:
        try:
            fetch_func = EXCHANGES[name]
            df = fetch_func(assets=ASSETS)
            df["Exchange"] = name
            data_frames.append(df)
            print(f"✅ Fetched from {name}: {len(df)} rows")
        except Exception as e:
            print(f"❌ Failed to fetch from {name}: {e}")

    if not data_frames:
        print("⚠️ No data fetched. Exiting.")
        return

    # รวมข้อมูลทั้งหมด
    combined_df = pd.concat(data_frames, ignore_index=True)

    # คำนวณ APY, Z-score, spread_per_day ฯลฯ
    processed_df = calculate_apy(combined_df)

    # บันทึกไฟล์ snapshot → .parquet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"arbitrage_snapshot_{timestamp}.parquet"
    filepath = save_snapshot(processed_df, filename)

    # อัปโหลดไปยัง Google Drive
    upload_to_gdrive(filepath, filename)

    print(f"✅ Snapshot completed and uploaded: {filename}")

if __name__ == "__main__":
    main()

