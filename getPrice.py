import requests
import pendulum
import pandas as pd


def get_current_time():
    # get current time rounded to 5 minutes (down)
    now = pendulum.now(tz='Asia/Ho_Chi_Minh')
    now = now.start_of('minute').subtract(minutes=now.minute % 5)
    return now


def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbols=["
    coins = ["BTC", "ETH", "BNB", "ADA", "XRP"]
    for coin in coins:
        url += "\"" + coin + "USDT\","
    url = url[:-1] + "]"
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    now = get_current_time()
    df['create_at'] = str(now)
    df['price'] = df['price'].astype(float)
    df["symbol"] = df["symbol"].astype(str)
    df['symbol'] = df['symbol'].str[:-4]

    print(df.head())
    df.to_csv('/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/price.csv', mode='a', header=False, index=False)


get_price()
