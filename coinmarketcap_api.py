import requests

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
API_HISTORICAL_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
API_KEY = "f9a40f0d-f3df-46a1-89ed-c1de9745fff3"  # کلید API خود را وارد کنید

def get_top_cryptocurrencies(limit=100):
    """
    Retrieves the top cryptocurrencies with the highest growth in the last 24 hours.

    Args:
        limit (int): Number of top cryptocurrencies to retrieve.

    Returns:
        list: A list of dictionaries containing cryptocurrency details.
    """
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "start": 1,
        "limit": 100,  # تعداد ارزهایی که می‌خواهید بررسی کنید
        "convert": "USD",
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            sorted_cryptos = sorted(
                data, key=lambda x: x["quote"]["USD"]["percent_change_24h"], reverse=True
            )
            return sorted_cryptos[:limit]
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
            return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def get_current_price(symbol):
    """
    Retrieves the current price of a cryptocurrency from CoinMarketCap.

    Args:
        symbol (str): The symbol of the cryptocurrency (e.g., 'BTC', 'ETH').

    Returns:
        float: The current price in USD, or None if there is an error.
    """
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "symbol": symbol,  # نماد ارز (مثل BTC, ETH, ... )
        "convert": "USD",  # تبدیل به دلار آمریکا
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        data = response.json()
        
        if response.status_code == 200:
            # استخراج قیمت اولین ارز در پاسخ
            price = data['data'][0]['quote']['USD']['price']
            return price
        else:
            print(f"Error fetching price: {data['status']['error_message']}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
def get_historical_price(symbol, timestamp):
    """
    Retrieves the historical price of a cryptocurrency at a specific timestamp.

    Args:
        symbol (str): Symbol of the cryptocurrency (e.g., BTC, ETH).
        timestamp (int): Unix timestamp for the desired time.

    Returns:
        float: Price of the cryptocurrency in USD at the given time.
    """
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "symbol": symbol,
        "time_start": timestamp,
        "time_end": timestamp + 3600,  # یک بازه 1 ساعته برای دریافت قیمت
        "interval": "hourly",  # دریافت قیمت ساعتی
        "convert": "USD",
    }
    try:
        response = requests.get(API_HISTORICAL_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if data and "quotes" in data:
                price = data["quotes"][-1]["quote"]["USD"]["price"]
                return price
        else:
            print(f"Error fetching historical price: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None