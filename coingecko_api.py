#coingecko_api.py
import requests
import time

def get_coin_id(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        coins = response.json()
        for coin in coins:
            if coin['symbol'].lower() == symbol.lower():
                return coin['id']
        print(f"Coin {symbol} not found in CoinGecko.")
        return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_historical_data(coin_id):
    to_timestamp = int(time.time())
    from_timestamp = to_timestamp - 24 * 60 * 60

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range?vs_currency=usd&from={from_timestamp}&to={to_timestamp}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'prices' in data:
            return data['prices']
        else:
            print(f"No price data available for {coin_id}.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_contract_address(coin_id):
    """
    دریافت آدرس قرارداد توکن با استفاده از CoinGecko.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        platforms = data.get("platforms", {})
        
        # بررسی اینکه آیا پلتفرم‌های اتریوم وجود دارد
        if 'ethereum' in platforms:
            contract_address = platforms['ethereum']  # آدرس قرارداد اتریوم
            print(f"Contract address for {coin_id}: {contract_address}")
            return contract_address
        else:
            print(f"No Ethereum contract address found for {coin_id}.")
            return None
    else:
        print(f"Error fetching data for {coin_id}: {response.status_code}")
        return None
