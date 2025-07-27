import requests
import pandas as pd
from datetime import datetime

def fetch_data(assets=["BTC", "ETH"]):
    data = []
    now = datetime.utcnow()

    # Endpoints
    endpoints = {
        "spot": "https://api.binance.com/api/v3/ticker/price",
        "perpetual": "https://fapi.binance.com/fapi/v1/premiumIndex",
        "futures": "https://dapi.binance.com/dapi/v1/premiumIndex",
    }

    # Fetch spot prices
    spot_prices = {}
    try:
        res = requests.get(endpoints["spot"], timeout=10)
        res.raise_for_status()
        for item in res.json():
            for asset in assets:
                if item["symbol"] == f"{asset}USDT":
                    spot_prices[asset] = float(item["price"])
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Spot: {e}")

    # Fetch perpetual
    try:
        res = requests.get(endpoints["perpetual"], timeout=10)
        res.raise_for_status()
        for item in res.json():
            for asset in assets:
                if item["symbol"] == f"{asset}USDT":
                    data.append({
                        "asset": asset,
                        "type": "perpetual",
                        "expiry": None,
                        "price": float(item["markPrice"]),
                        "spot_price": spot_prices.get(asset),
                    })
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Perpetual: {e}")

    # Fetch futures (delivery)
    try:
        res = requests.get(endpoints["futures"], timeout=10)
        res.raise_for_status()
        for item in res.json():
            for asset in assets:
                if item["symbol"].startswith(asset):
                    expiry = datetime.fromtimestamp(item["deliveryDate"] / 1000)
                    if expiry > now:
                        data.append({
                            "asset": asset,
                            "type": "futures",
                            "expiry": expiry.strftime("%Y-%m-%d"),
                            "price": float(item["markPrice"]),
                            "spot_price": spot_prices.get(asset),
                        })
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Futures: {e}")

    return pd.DataFrame(data)
