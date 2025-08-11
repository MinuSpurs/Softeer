#!/usr/bin/env python3
import sys

for line in sys.stdin:
    if line.startswith("userId"):  # 헤더 무시
        continue
    parts = line.strip().split(",")
    if len(parts) >= 3:
        movie_id = parts[1]
        rating = parts[2]
        print(f"{movie_id}\t{rating}")