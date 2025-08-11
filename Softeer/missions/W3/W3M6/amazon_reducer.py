#!/usr/bin/env python3
import sys

current_product = None
total_rating = 0.0
review_count = 0

for line in sys.stdin:
    product_id, rating = line.strip().split("\t")
    rating = float(rating)

    if current_product == product_id:
        total_rating += rating
        review_count += 1
    else:
        if current_product is not None:
            avg = total_rating / review_count
            print(f"{current_product}\t{review_count}\t{avg:.2f}")
        current_product = product_id
        total_rating = rating
        review_count = 1

if current_product is not None:
    avg = total_rating / review_count
    print(f"{current_product}\t{review_count}\t{avg:.2f}")