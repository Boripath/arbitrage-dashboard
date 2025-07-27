# fetch/__init__.py
# ไว้สำหรับรวมการโหลดโมดูลภายในโฟลเดอร์ fetch

from .fetch_deribit import fetch_deribit
from .fetch_binance import fetch_data as fetch_binance
from .fetch_bybit import fetch_data as fetch_bybit

