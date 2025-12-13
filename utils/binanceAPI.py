import requests

def get_binance_ticker(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        return requests.get(url, timeout=3).json()
    except:
        return None

def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=24"
        data = requests.get(url, timeout=3).json()
        return data
    except:
        return []