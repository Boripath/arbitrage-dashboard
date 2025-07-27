import requests
import pandas as pd
from datetime import datetime

def fetch_data(assets=["BTC", "ETH"]):
    base_url = "https://www.deribit.com/api/v2/public/get_instruments"
    result = []

    for asset in assets:
        for kind in ["future", "perpetual"]:
            params = {
                "currency": asset,
                "kind": kind,
                "expired": False
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            instruments = response.json()["result"]

            for inst in instruments:
                instrument_name = inst["instrument_name"]
                type_ = inst["instrument_type"]
                expiry = inst.get("expiration_timestamp")
                if expiry:
                    expiry = datetime.utcfromtimestamp(expiry / 1000).strftime("%Y-%m-%d")
                else:
                    expiry = "perpetual"

                # Get mark price
                mark_resp = requests.get("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument", params={"instrument_name": instrument_name})
                mark_resp.raise_for_status()
                mark_price = mark_resp.json()["result"][0]["mark_price"]

                # Get spot price (using perpetual if available)
                spot_instrument = f"{asset}-PERPETUAL"
                spot_resp = requests.get("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument", params={"instrument_name": spot_instrument})
                spot_resp.raise_for_status()
                spot_price = spot_resp.json()["result"][0]["mark_price"]

                result.append({
                    "asset": asset,
                    "type": type_,
                    "expiry": expiry,
                    "price": mark_price,
                    "spot_price": spot_price
                })

    return pd.DataFrame(result)

