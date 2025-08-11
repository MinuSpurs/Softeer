#!/usr/bin/env python3
import sys

current_sentiment = None
count = 0

for line in sys.stdin:
    sentiment, c = line.strip().split("\t", 1)
    c = int(c)

    if current_sentiment == sentiment:
        count += c
    else:
        if current_sentiment is not None:
            print(f"{current_sentiment}\t{count}")
        current_sentiment = sentiment
        count = c

if current_sentiment is not None:
    print(f"{current_sentiment}\t{count}")