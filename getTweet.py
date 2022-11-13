import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
import pendulum
import string
import re

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
tokenizer = AutoTokenizer.from_pretrained("/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/manhnk-model")
model = AutoModelForSequenceClassification.from_pretrained("/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/manhnk-model")
model.save_pretrained("manhnk-model")


def get_current_time():
    # get current time rounded to 5 minutes (down)
    now = pendulum.now(tz='Asia/Ho_Chi_Minh')
    now = now.start_of('minute').subtract(minutes=now.minute % 5)
    return now


def preprocess(text):
    def remove_hyperlink(word):
        return re.sub(r"http\S+", "", word)

    def to_lower(word):
        result = word.lower()
        return result

    def remove_number(word):
        result = re.sub(r'\d+', '', word)
        return result

    def remove_punctuation(word):
        result = word.translate(str.maketrans(dict.fromkeys(string.punctuation)))
        return result

    def remove_whitespace(word):
        result = word.strip()
        return result

    def replace_newline(word):
        return word.replace('\n', '')

    def clean_up_pipeline(sentence):
        cleaning_utils = [remove_hyperlink,
                          replace_newline,
                          to_lower,
                          remove_number,
                          remove_punctuation, remove_whitespace]
        for o in cleaning_utils:
            sentence = o(sentence)
        return sentence

    return clean_up_pipeline(text)


def get_sentiment_point(text):
    encoded_input = tokenizer(preprocess(text), return_tensors='pt')
    output = model(**encoded_input)
    scores = softmax(output[0].detach().numpy())
    # get index of max score
    rank = np.argmax(scores)
    if rank == 0:  # negative
        return -1
    elif rank == 1:  # neutral
        return 0
    else:  # positive
        return 1


now = get_current_time()
now_timestamp = int(now.timestamp())
query = "(#BTC OR #ETH OR #BNB OR #XRP OR #ADA) lang:en since_time:" + str(now_timestamp)
counter = {
    "btc": [0, 0],
    "eth": [0, 0],
    "bnb": [0, 0],
    "xrp": [0, 0],
    "ada": [0, 0]
}  # [trend_point, sentiment_point]
result = []

logging.info("Start scraping")
logging.info("Query: " + query)
for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    # get sentiment point
    sentiment_point = get_sentiment_point(tweet.content)

    hashtags = tweet.hashtags
    for hashtag in hashtags:
        hashtag = hashtag.lower()
        if hashtag in counter:
            counter[hashtag][0] += 1
            counter[hashtag][1] += sentiment_point

result.append({"symbol": "BTC", "trend_point": counter["btc"][0], "sentiment_point": counter["btc"][1], "created_at": str(now)})
result.append({"symbol": "ETH", "trend_point": counter["eth"][0], "sentiment_point": counter["eth"][1], "created_at": str(now)})
result.append({"symbol": "BNB", "trend_point": counter["bnb"][0], "sentiment_point": counter["bnb"][1], "created_at": str(now)})
result.append({"symbol": "XRP", "trend_point": counter["xrp"][0], "sentiment_point": counter["xrp"][1], "created_at": str(now)})
result.append({"symbol": "ADA", "trend_point": counter["ada"][0], "sentiment_point": counter["ada"][1], "created_at": str(now)})


df = pd.DataFrame.from_dict(result)
print(df)

df.to_csv("/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/result.csv", index=False, mode="a", header=False)
