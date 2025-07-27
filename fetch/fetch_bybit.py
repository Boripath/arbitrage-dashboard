import requests
import pandas as pd
from datetime import datetime

def fetch_bybit(assets=["BTC", "ETH"]):
    data = []
    now = datetime.utcnow()

    # Map assets to Bybit symbols
    spot_symbols = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}

    # Spot Prices
    spot_prices = {}
    try:
        for asset in assets:
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={spot_symbols[asset]}"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            result = res.json()['result']
            if 'list' in result:
                price = float(result['list'][0]['lastPrice'])
                spot_prices[asset] = price
    except Exception as e:
        raise RuntimeError(f"Bybit Spot failed: {e}")

    # Perpetual Contracts (Linear)
    try:
        for asset in assets:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={asset}USDT"  # e.g., BTCUSDT
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            result = res.json()['result']
            if 'list' in result:
                price = float(result['list'][0]['markPrice'])
                data.append({
                    "asset": asset,
                    "type": "perpetual",
                    "expiry": None,
                    "price": price,
                    "spot_price": spot_prices.get(asset)
                })
    except Exception as e:
        raise RuntimeError(f"Bybit Perpetual failed: {e}")

    # Futures (Inverse, with expiry)
    try:
        url = "https://api.bybit.com/v5/market/tickers?category=inverse"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        result = res.json()['result']
        if 'list' in result:
            for item in result['list']:
                for asset in assets:
                    if item['symbol'].startswith(asset) and item['symbol'].endswith("USD") and len(item['symbol']) > len(asset) + 3:
                        expiry_str = item['symbol'][len(asset):-3]  # e.g., 250627 from BTC250627USD
                        try:
                            expiry = datetime.strptime(expiry_str, "%y%m%d")
                            if expiry > now:
                                data.append({
                                    "asset": asset,
                                    "type": "futures",
                                    "expiry": expiry.strftime("%Y-%m-%d"),
                                    "price": float(item['markPrice']),
                                    "spot_price": spot_prices.get(asset)
                                })
                        except:
                            continue
    except Exception as e:
        raise RuntimeError(f"Bybit Futures failed: {e}")

    return pd.DataFrame(data)

