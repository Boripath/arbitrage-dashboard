import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_binance(assets=["BTC", "ETH"]):
    data = []
    now = datetime.utcnow()

    # Define endpoints
    endpoints = {
        "spot": "https://api.binance.com/api/v3/ticker/price",
        "perpetual": "https://fapi.binance.com/fapi/v1/premiumIndex",
        "futures": "https://dapi.binance.com/dapi/v1/premiumIndex",
    }

    # Spot Prices
    spot_prices = {}
    try:
        response = requests.get(endpoints["spot"], timeout=10)
        response.raise_for_status()
        for item in response.json():
            for asset in assets:
                if item['symbol'] == f"{asset}USDT":
                    spot_prices[asset] = float(item['price'])
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Spot: {e}")

    # Perpetual Contracts
    try:
        response = requests.get(endpoints["perpetual"], timeout=10)
        response.raise_for_status()
        for item in response.json():
            for asset in assets:
                if item['symbol'] == f"{asset}USDT":
                    data.append({
                        "asset": asset,
                        "type": "perpetual",
                        "expiry": None,
                        "price": float(item['markPrice']),
                        "spot_price": spot_prices.get(asset, None),
                    })
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Perpetual: {e}")

    # Delivery Futures
    try:
        response = requests.get(endpoints["futures"], timeout=10)
        response.raise_for_status()
        for item in response.json():
            for asset in assets:
                if item['symbol'].startswith(asset):
                    exp_str = item['symbol'].replace(asset, '').replace("USD", "")
                    expiry = datetime.strptime(exp_str, "%y%m%d")
                    if expiry > now:
                        data.append({
                            "asset": asset,
                            "type": "futures",
                            "expiry": expiry.strftime("%Y-%m-%d"),
                            "price": float(item['markPrice']),
                            "spot_price": spot_prices.get(asset, None),
                        })
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Binance Futures: {e}")

    return pd.DataFrame(data)

