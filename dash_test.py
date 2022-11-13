import pandas as pd
import pendulum

def get_current_time():
    # get current time rounded to 5 minutes (down)
    now = pendulum.now(tz='Asia/Ho_Chi_Minh')
    now = now.start_of('minute').subtract(minutes=now.minute % 5)
    return now



df_price = pd.read_csv('/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/price.csv',
                       names=['symbol', 'price', 'create_at'])
df_tweet = pd.read_csv('/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/result.csv',
                       names=['symbol', 'trend_point', 'sentiment_point', 'create_at'])
df_tweet['create_at'] = pd.to_datetime(df_tweet['create_at'])
df_price['create_at'] = pd.to_datetime(df_price['create_at'])

now = get_current_time()
# get record in df_price with create_at = now
df_price_now = df_price[df_price['create_at'] == now]
# get record in df_tweet with create_at = now
df_tweet_now = df_tweet[df_tweet['create_at'] == now]

print(df_price_now)
print(df_tweet_now)