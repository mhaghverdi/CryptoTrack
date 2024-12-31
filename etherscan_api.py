import aiohttp  # وارد کردن aiohttp برای استفاده از درخواست‌های غیرهمزمان

ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_API_KEY = "KDPRZJNTZ34DIUYRDW6NF58CBNBRW449QP"

async def get_wallet_transactions(wallet_address):
    # پارامترهای درخواست برای دریافت تراکنش‌های کیف پول
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 100,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }

    # استفاده از aiohttp برای ارسال درخواست به API به صورت غیرهمزمان
    async with aiohttp.ClientSession() as session:
        async with session.get(ETHERSCAN_API_URL, params=params) as response:
            data = await response.json()

    # بررسی وضعیت درخواست
    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error: {data['message']}")
        return []

async def get_normal_transactions(address, start_timestamp, end_timestamp):
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 100,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }

    # استفاده از aiohttp برای ارسال درخواست به API به صورت غیرهمزمان
    async with aiohttp.ClientSession() as session:
        async with session.get(ETHERSCAN_API_URL, params=params) as response:
            data = await response.json()

    # بررسی وضعیت درخواست
    if data["status"] == "1":
        transactions = data["result"]
        recent_transactions = []

        for tx in transactions:
            timestamp = int(tx["timeStamp"])
            if start_timestamp <= timestamp <= end_timestamp:  # محدود کردن به 24 ساعت گذشته
                recent_transactions.append(tx)

        return recent_transactions
    else:
        print(f"Error: {data['message']}")
        return []
