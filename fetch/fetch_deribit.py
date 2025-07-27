import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://www.deribit.com/api/v2/public/get_instruments"
TICKER_URL = "https://www.deribit.com/api/v2/public/ticker"


def fetch_data(assets=["BTC", "ETH"]):
    result = []
    now = datetime.utcnow()

    for asset in assets:
        try:
            # 1. Get Futures Instruments (non-expired)
            instruments_resp = requests.get(BASE_URL, params={
                "currency": asset,
                "kind": "future",
                "expired": "false"  # must be string lowercase
            }, timeout=10)
            instruments_resp.raise_for_status()
            instruments = instruments_resp.json()["result"]

            for inst in instruments:
                instrument_name = inst["instrument_name"]
                expiry_ts = inst["expiration_timestamp"] // 1000
                expiry = datetime.utcfromtimestamp(expiry_ts)
                days_to_expiry = (expiry - now).days

                # 2. Get Mark Price
                ticker_resp = requests.get(TICKER_URL, params={"instrument_name": instrument_name}, timeout=10)
                ticker_resp.raise_for_status()
                mark_price = ticker_resp.json()["result"]["mark_price"]
                index_price = ticker_resp.json()["result"].get("index_price")

                result.append({
                    "asset": asset,
                    "type": "futures",
                    "expiry": expiry.strftime("%Y-%m-%d"),
                    "price": mark_price,
                    "spot_price": index_price,
                })

        except Exception as e:
            raise RuntimeError(f"Deribit failed for {asset}: {e}")

    return pd.DataFrame(result)
