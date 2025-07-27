import pandas as pd
from scipy.stats import zscore
from datetime import datetime

def calculate_apy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # คำนวณจำนวนวันจนหมดอายุ
    def days_to_expiry(row):
        if row["type"] == "perpetual" or row["expiry"] is None:
            return 1  # สมมติให้ perpetual มีอายุ 1 วันเพื่อใช้คำนวณ APY
        expiry = pd.to_datetime(row["expiry"])
        delta = (expiry - datetime.utcnow()).days
        return max(delta, 1)

    df["days_to_expiry"] = df.apply(days_to_expiry, axis=1)

    # คำนวณ spread และ APY
    df["spread"] = df["price"] - df["spot_price"]
    df["apy_daily"] = df["spread"] / df["spot_price"]
    df["apy_annual"] = df["apy_daily"] * (365 / df["days_to_expiry"])

    # คำนวณ Z-score ของ APY Annual (ตาม asset + type)
    df["zscore"] = df.groupby(["asset", "type"])["apy_annual"].transform(zscore)

    return df
