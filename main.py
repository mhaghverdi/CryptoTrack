import asyncio
import time
import os

# تست نوشتن در فایل برای بررسی دسترسی‌ها
try:
    with open("validated_wallets.txt", "a") as file:
        file.write("Test wallet address\n")
    print("File write test successful!")
except Exception as e:
    print(f"Error during test file write: {e}")

from colorama import Fore, init
from coinmarketcap_api import get_top_cryptocurrencies
from coingecko_api import get_coin_id, get_historical_data, get_contract_address
from etherscan_api import get_normal_transactions, get_wallet_transactions
from cryptocompare_api import get_24h_price_with_interval, find_pumps
from datetime import datetime

# برای فعال کردن رنگ‌ها در ترمینال
init(autoreset=True)

REQUEST_DELAY = 60  # فاصله بین درخواست‌ها به ثانیه

async def process_wallet(wallet_address, start_time, end_time):
    """بررسی تراکنش‌های مربوط به یک کیف پول"""
    print(f"Checking transactions for wallet: {wallet_address}")
    wallet_transactions = await get_wallet_transactions(wallet_address)
    
    if wallet_transactions:
        print(f"Transactions for wallet {wallet_address}:")
        buy_transaction = None
        sell_transaction = None
        
        for tx in wallet_transactions:
            tx_timestamp = int(tx['timeStamp'])
            print(f"- From: {tx['from']}, To: {tx['to']}, Timestamp: {tx_timestamp}")
            
            # بررسی تراکنش‌های خرید (کیف پول به قرارداد) و فروش (قرارداد به کیف پول)
            if start_time and end_time:
                # بررسی تراکنش خرید: باید قبل از شروع پامپ باشد
                if tx['from'] == wallet_address and start_time.timestamp() - 3600 <= tx_timestamp <= start_time.timestamp():
                    print(Fore.YELLOW + f"Buy transaction for wallet {wallet_address} before pump start: {tx}")
                
                # بررسی تراکنش فروش: باید بعد از پایان پامپ باشد
                if tx['to'] == wallet_address and end_time.timestamp() <= tx_timestamp <= end_time.timestamp() + 3600:
                    print(Fore.YELLOW + f"Sell transaction for wallet {wallet_address} after pump end: {tx}")

    else:
        print(f"No transactions found for wallet {wallet_address}.")

async def process_cryptocurrency(crypto, request_queue):
    """بررسی اطلاعات ارز و تراکنش‌های مرتبط"""
    name = crypto["name"]
    symbol = crypto["symbol"]
    change_24h = crypto["quote"]["USD"]["percent_change_24h"]
    volume_24h = crypto["quote"]["USD"]["volume_24h"]  # حجم معاملات در 24 ساعت گذشته

    print(f"Name: {name}, Symbol: {symbol}, Change (24h): {change_24h}%, Volume (24h): {volume_24h}")

    # بررسی حجم معاملات (اگر حجم معاملات بیشتر از یک میلیون دلار بود، ادامه بدیم)
    if volume_24h < 1000000:
        print(f"Volume for {name} ({symbol}) is less than 1 million USD. Skipping...")
        return

    coin_id = get_coin_id(symbol)
    if not coin_id:
        print(f"Coin ID for {name} ({symbol}) not found in CoinGecko.")
        return
    
    # استفاده از API CryptoCompare برای گرفتن قیمت‌ها
    print(f"Getting 24h price data for {name} ({symbol})...")
    prices = get_24h_price_with_interval(symbol)
    if not prices:
        print(f"No price data found for {name} ({symbol}).")
        return

    # یافتن زمان‌های شروع و پایان پامپ
    start_time, end_time = find_pumps(prices)
    if start_time and end_time:
        print(f"Price pump for {name} ({symbol}) occurred from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"No price pump found for {name} ({symbol}).")

    contract_address = get_contract_address(coin_id)
    if not contract_address:
        print(f"No Ethereum contract address found for {symbol}. Skipping to next cryptocurrency.")
        return

    print(f"Ethereum contract address for {name} ({symbol}): {contract_address}")
    current_time = int(time.time())
    start_time_timestamp = current_time - 24 * 60 * 60

    transactions = await get_normal_transactions(contract_address, start_time_timestamp, current_time)
    if transactions:
        print(f"Transactions for {name} ({symbol}):")
        wallet_addresses = set()
        for tx in transactions:
            print(f"- From: {tx['from']}, To: {tx['to']}, Timestamp: {tx['timeStamp']}")
            wallet_addresses.add(tx['from'])
            wallet_addresses.add(tx['to'])

        for wallet_address in wallet_addresses:
             await request_queue.put((process_wallet, (wallet_address, start_time, end_time), f"Wallet transactions for {wallet_address}"))
    else:
        print(f"No transactions found for {name} ({symbol}).")

async def request_worker(request_queue):
    """کارگر صف که درخواست‌ها را با تاخیر پردازش می‌کند"""
    while True:
        func, args, description = await request_queue.get()
        try:
            print(f"Processing: {description}")
            await func(*args)
        except Exception as e:
            print(f"Error in {description}: {e}")
        finally:
            request_queue.task_done()
        await asyncio.sleep(1)  # فاصله 2 ثانیه‌ای برای پردازش کیف پول‌ها

async def main():
    print("Starting CoinMarketCap Tracker Project")

    # مرحله 1: دریافت اطلاعات ارزها
    top_cryptos = get_top_cryptocurrencies()
    print("Top Cryptocurrencies with Highest Growth in the Last 24 Hours:")

    if not top_cryptos:
        print("No top cryptocurrencies data available. Exiting.")
        return

    request_queue = asyncio.Queue()

    # ایجاد تسک برای کارگر صف
    worker_task = asyncio.create_task(request_worker(request_queue))

    for crypto in top_cryptos:
        print(f"Processing cryptocurrency: {crypto['name']} ({crypto['symbol']})")
        try:
            await process_cryptocurrency(crypto, request_queue)
            # بررسی تمام کیف پول‌ها قبل از رفتن به ارز بعدی
            print("Waiting for all wallet transactions to be processed before moving to the next cryptocurrency...")
            await request_queue.join()  # اطمینان از پردازش تمام کیف پول‌ها
        except Exception as e:
            print(f"Error processing cryptocurrency {crypto['name']}: {e}")
        finally:
            print("Waiting for 60 seconds before processing the next cryptocurrency...")
            await asyncio.sleep(60)  # فاصله 60 ثانیه برای پردازش ارزها


    worker_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
