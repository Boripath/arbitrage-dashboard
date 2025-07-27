import requests
import pandas as pd
from datetime import datetime

def fetch_data(assets=["BTC", "ETH"]):
    data = []
    now = datetime.utcnow()

    # Spot prices
    spot_prices = {}
    try:
        res = requests.get("https://api.bybit.com/v2/public/tickers", timeout=10)
        res.raise_for_status()
        for item in res.json()["result"]:
            for asset in assets:
                if item["symbol"] == f"{asset}USDT":
                    spot_prices[asset] = float(item["last_price"])
    except Exception as e:
        raise RuntimeError(f"Bybit Spot failed: {e}")

    # Futures and Perpetual
    try:
        res = requests.get("https://api.bybit.com/v5/market/tickers?category=linear", timeout=10)
        res.raise_for_status()
        for item in res.json()["result"]["list"]:
            symbol = item["symbol"]
            for asset in assets:
                if asset in symbol:
                    contract_type = "perpetual" if "PERP" in symbol else "futures"
                    expiry = None if contract_type == "perpetual" else symbol.split("-")[-1]
                    data.append({
                        "asset": asset,
                        "type": contract_type,
                        "expiry": expiry,
                        "price": float(item["markPrice"]),
                        "spot_price": spot_prices.get(asset),
                    })
    except Exception as e:
        raise RuntimeError(f"Bybit Futures failed: {e}")

    return pd.DataFrame(data)
