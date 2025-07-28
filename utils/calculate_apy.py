import pandas as pd
import numpy as np
from scipy.stats import zscore


def calculate_apy(df: pd.DataFrame) -> pd.DataFrame:
    def days_to_expiry(row):
        try:
            # รองรับทั้ง timestamp (ms) และ string
            if isinstance(row["expiry"], (int, float)):
                expiry = pd.to_datetime(row["expiry"], unit="ms", errors="coerce")
            else:
                expiry = pd.to_datetime(row["expiry"], errors="coerce")

            if pd.isnull(expiry):
                return np.nan

            days = (expiry - pd.Timestamp.now()).days
            return max(days, 1)  # ป้องกันหารด้วย 0 หรือค่าติดลบ
        except:
            return np.nan

    # คำนวณ days_to_expiry
    df["days_to_expiry"] = df.apply(days_to_expiry, axis=1)

    # คำนวณ Spread และ APY
    df["spread"] = df["future_price"] - df["spot_price"]
    df["apy"] = (df["spread"] / df["spot_price"]) * (365 / df["days_to_expiry"])

    # Z-score ของ APY
    df["zscore"] = zscore(df["apy"].fillna(0))

    return df
