#cryptocompare_api.py
import requests
import time
from datetime import datetime, timedelta  # اضافه شد

API_KEY = '459d30b5ea5cbe26c764417f6d90fb2e1890384e101d4ef4d8772b5f61614eda'

def get_24h_price_with_interval(crypto_symbol):
    url = 'https://min-api.cryptocompare.com/data/histominute'
    params = {
        'fsym': crypto_symbol,
        'tsym': 'USD',
        'limit': 1440,  # 1 دقیقه‌ای برای 24 ساعت
        'toTs': int(time.time()),
        'api_key': API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if 'Data' in data:
            prices = [entry['close'] for entry in data['Data']]
            return prices
        else:
            print(f"Error: {data.get('Message', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def find_pumps(prices):
    min_price = min(prices)
    max_price = max(prices)
    price_diff = max_price - min_price
    
    min_bound = min_price + (price_diff * 0.05)
    max_bound = max_price - (price_diff * 0.05)
    
    print(f"Min price: {min_price}, Max price: {max_price}")
    print(f"Price difference: {price_diff}")
    print(f"Min bound (5% of price difference above min): {min_bound}")
    print(f"Max bound (5% of price difference below max): {max_bound}")
    
    start_index = None
    end_index = None

    for i in range(len(prices)):
        if prices[i] >= max_bound and end_index is None:
            end_index = i  # ذخیره اولین نقطه‌ای که به کران بالایی می‌رسد
            break

    if end_index is not None:
        for j in range(end_index - 1, -1, -1):  # حرکت به عقب از نقطه پایان پامپ
            if prices[j] <= min_bound:  # جایی که قیمت به کران پایین می‌رسد
                start_index = j
                break

    if start_index is not None and end_index is not None:
        start_minutes_ago = len(prices) - start_index
        end_minutes_ago = len(prices) - end_index

        start_hours, start_minutes = divmod(start_minutes_ago, 60)
        end_hours, end_minutes = divmod(end_minutes_ago, 60)

        # محاسبه زمان دقیق با توجه به ساعت و دقیقه به دست آمده
        current_time = datetime.now()

        start_time = current_time - timedelta(hours=start_hours, minutes=start_minutes)
        end_time = current_time - timedelta(hours=end_hours, minutes=end_minutes)

        return start_time.strftime('%Y-%m-%d %H:%M'), end_time.strftime('%Y-%m-%d %H:%M')
    else:
        return None, None
