#main.py
import asyncio
import time
from cryptocompare_api import get_24h_price_with_interval, find_pumps
from colorama import Fore, init
from coinmarketcap_api import get_top_cryptocurrencies
from etherscan_api import get_wallet_transactions

# برای فعال کردن رنگ‌ها در ترمینال
init(autoreset=True)

REQUEST_DELAY = 60  # فاصله بین درخواست‌ها به ثانیه

async def process_wallet(wallet_address):
    """بررسی تراکنش‌های مربوط به یک کیف پول"""
    print(f"Checking transactions for wallet: {wallet_address}")
    wallet_transactions = await get_wallet_transactions(wallet_address)
    
    if wallet_transactions:
        print(f"Transactions for wallet {wallet_address}:")
        buy_transaction = None
        sell_transaction = None
        
        for tx in wallet_transactions:
            print(f"- From: {tx['from']}, To: {tx['to']}, Timestamp: {tx['timeStamp']}")
            
            # فرض می‌کنیم که خرید و فروش از قرارداد خاصی می‌باشد
            # تراکنش خرید: از کیف پول به قرارداد (From = Wallet, To = Contract)
            # تراکنش فروش: از قرارداد به کیف پول (From = Contract, To = Wallet)
            if tx['to'] == wallet_address:  # تراکنش فروش (قرارداد به کیف پول)
                sell_transaction = tx
            elif tx['from'] == wallet_address:  # تراکنش خرید (کیف پول به قرارداد)
                buy_transaction = tx
        
        # بررسی اینکه آیا خرید و فروش انجام شده و مقدار ارزهای خرید و فروش برابر است
        if buy_transaction and sell_transaction:
            if buy_transaction['value'] == sell_transaction['value']:
                print(Fore.GREEN + f"Wallet {wallet_address} has a valid buy and sell transaction.")
                # ذخیره کردن آدرس کیف پول تایید شده در فایل
                with open("validated_wallets.txt", "a") as file:
                    file.write(f"{wallet_address}\n")
                print(Fore.RED + f"Wallet {wallet_address} has been saved to validated_wallets.txt.")
            else:
                print(Fore.RED + f"Wallet {wallet_address} has buy and sell transactions with unequal amounts.")
        else:
            print(Fore.RED + f"Wallet {wallet_address} does not have both buy and sell transactions.")
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

    # ادامه پردازش
    price_data = get_24h_price_with_interval(symbol)
    if price_data:
        #print(f"Price data for {name} ({symbol}): {price_data}")
        start_time, end_time = find_pumps(price_data)
        if start_time and end_time:
            print(Fore.GREEN + f"Pump from {start_time} to {end_time}")
            print(Fore.GREEN + f"------------------------------------")
            # جستجو و بررسی تراکنش‌ها در بازه زمانی مشخص
        else:
            print("No pump detected.")
    else:
        print(f"No price data found for {name} ({symbol}).")

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
