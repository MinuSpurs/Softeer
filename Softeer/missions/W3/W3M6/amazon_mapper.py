#!/usr/bin/env python3
import sys
import json

for line in sys.stdin:
    try:
        data = json.loads(line)
        product_id = data.get("asin")
        rating = data.get("rating")

        if product_id and rating:
            print(f"{product_id}\t{rating}")
    except json.JSONDecodeError:
        continue  # JSON 파싱 실패 시 무시