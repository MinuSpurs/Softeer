#!/usr/bin/env python3
import sys
from textblob import TextBlob

def classify_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

for line in sys.stdin:
    if line.startswith("target,"):
        continue
    line = line.strip()
    parts = line.split(",", 5)
    if len(parts) == 6:
        tweet = parts[5].strip().strip('"')
        sentiment = classify_sentiment(tweet)
        print(f"{sentiment}\t1")