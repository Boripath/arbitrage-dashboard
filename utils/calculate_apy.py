import pandas as pd
import numpy as np
from datetime import datetime

def calculate_apy(df: pd.DataFrame) -> pd.DataFrame:
    """
    คำนวณ APY และ Z-score ของแต่ละคู่ asset (Spot vs Futures หรือ Perpetual)
    :param df: DataFrame ที่มีคอลัมน์ [asset, type, expiry, price, spot_price]
    :return: DataFrame ที่มีคอลัมน์เพิ่ม [premium_pct, days_to_expiry, apy_daily, apy_annual, zscore_apy]
    """
    df = df.copy()
    now = datetime.utcnow()

    # Premium (%)
    df["premium_pct"] = (df["price"] - df["spot_price"]) / df["spot_price"]

    # Days to Expiry (ใช้ 1 วันแทนสำหรับ perpetual)
    df["days_to_expiry"] = df["expiry"].apply(
        lambda x: 1 if x is None or pd.isna(x) else max((datetime.strptime(x, "%Y-%m-%d") - now).days, 1)
    )

    # APY รายวัน / รายปี
    df["apy_daily"] = df["premium_pct"] / df["days_to_expiry"]
    df["apy_annual"] = df["apy_daily"] * 365

    # คำนวณ Z-score ของ APY Annual ตาม asset และประเภท (perpetual/futures)
    df["zscore_apy"] = df.groupby(["asset", "type"])["apy_annual"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=0) if len(x) > 1 and x.std(ddof=0) > 0 else 0
    )

    return df.sort_values("apy_annual", ascending=False).reset_index(drop=True)

