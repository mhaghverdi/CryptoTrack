# cryptocompare_api.py
import requests

API_URL_PRICE = "https://min-api.cryptocompare.com/data/price"
API_URL_HISTORICAL = "https://min-api.cryptocompare.com/data/v2/histoday"
API_KEY = "459d30b5ea5cbe26c764417f6d90fb2e1890384e101d4ef4d8772b5f61614eda"  # کلید API شما

def get_current_price(symbol, currency="USD"):
    """
    Retrieves the current price of a cryptocurrency from CryptoCompare.

    Args:
        symbol (str): The symbol of the cryptocurrency (e.g., 'BTC', 'ETH').
        currency (str): The fiat currency to convert to (default is 'USD').

    Returns:
        float: The current price of the cryptocurrency in the specified currency.
    """
    url = f"{API_URL_PRICE}?fsym={symbol}&tsyms={currency}"
    headers = {
        'Authorization': f"Apikey {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get(currency)
        else:
            print(f"Error fetching price: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def get_historical_data(symbol, limit=30, currency="USD"):
    """
    Retrieves historical data for a cryptocurrency from CryptoCompare.

    Args:
        symbol (str): The symbol of the cryptocurrency (e.g., 'BTC', 'ETH').
        limit (int): The number of data points to retrieve (default is 30 days).
        currency (str): The fiat currency to convert to (default is 'USD').

    Returns:
        list: A list of historical data points, or an empty list if an error occurs.
    """
    url = f"{API_URL_HISTORICAL}?fsym={symbol}&tsym={currency}&limit={limit}"
    headers = {
        'Authorization': f"Apikey {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('Data', {}).get('Data', [])
            return data
        else:
            print(f"Error fetching historical data: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []
