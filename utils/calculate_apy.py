import pandas as pd
import numpy as np
from scipy.stats import zscore

def calculate_apy(df: pd.DataFrame) -> pd.DataFrame:
    def days_to_expiry(row):
        try:
            if isinstance(row["expiry"], (int, float)):
                expiry = pd.to_datetime(row["expiry"], unit="ms", errors="coerce")
            else:
                expiry = pd.to_datetime(row["expiry"], errors="coerce")

            if pd.isnull(expiry):
                return np.nan

            days = (expiry - pd.Timestamp.now()).days
            return max(days, 1)
        except:
            return np.nan

    # คำนวณ days_to_expiry
    df["days_to_expiry"] = df.apply(days_to_expiry, axis=1)

    # ใช้ชื่อ future_col ให้รองรับทั้ง price และ future_price
    future_col = "future_price" if "future_price" in df.columns else "price"
    df["spread"] = df[future_col] - df["spot_price"]

    # คำนวณ APY
    df["apy_daily"] = df["spread"] / df["spot_price"] / df["days_to_expiry"]
    df["apy_annual"] = df["apy_daily"] * 365

    # Z-score
    df["zscore"] = zscore(df["apy_annual"].fillna(0))

    return df
