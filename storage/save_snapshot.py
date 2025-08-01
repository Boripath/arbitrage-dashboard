# 📁 storage/save_snapshot.py
import os
import pandas as pd

def save_snapshot(df: pd.DataFrame, filename: str, folder: str = "data") -> str:
    """
    Save the given DataFrame to a Parquet file in the specified folder.
    Returns the full file path.
    """
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    df.to_parquet(filepath, index=False)
    print(f"💾 Saved snapshot to: {filepath}")
    return filepath
