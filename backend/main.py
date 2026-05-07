import time
import requests
import mysql.connector

while True:

    # Fetch Binance BTC price
    binance_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    binance_response = requests.get(binance_url)
    binance_data = binance_response.json()

    binance_price = float(binance_data["price"])

    # Fetch Bybit BTC price
    bybit_url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"

    bybit_response = requests.get(bybit_url)
    bybit_data = bybit_response.json()

    bybit_price = float(bybit_data["result"]["list"][0]["lastPrice"])

    print("Binance Price:", binance_price)
    print("Bybit Price:", bybit_price)

    # Calculate arbitrage
    spread = bybit_price - binance_price
    profit_percent = (spread / binance_price) * 100

    print("Spread:", spread)
    print("Profit %:", profit_percent)

    # Connect MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ayush123",
        database="arbitrage_system"
    )

    cursor = db.cursor()

    # Store prices
    price_query = """
    INSERT INTO prices (exchange_name, symbol, price)
    VALUES (%s, %s, %s)
    """

    cursor.execute(price_query, ("Binance", "BTCUSDT", binance_price))

    cursor.execute(price_query, ("Bybit", "BTCUSDT", bybit_price))

    # Store arbitrage opportunity
    arb_query = """
    INSERT INTO arbitrage_opportunities
    (buy_exchange, sell_exchange, symbol,
    buy_price, sell_price, spread, profit_percent)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        "Binance",
        "Bybit",
        "BTCUSDT",
        binance_price,
        bybit_price,
        spread,
        profit_percent
    )

    cursor.execute(arb_query, values)

    db.commit()

    print("""
==============================
ARBITRAGE OPPORTUNITY
==============================
""")

    print(f"BUY  -> Binance : {binance_price}")
    print(f"SELL -> Bybit   : {bybit_price}")

    print(f"""
SPREAD   : {spread}
PROFIT % : {profit_percent}
""")

    print("Stored successfully\n")

    time.sleep(5)