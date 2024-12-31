#coinmarketcap_api.py
import requests

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
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