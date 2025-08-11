#!/usr/bin/env python3
import sys

current_movie = None
total_rating = 0.0
count = 0

for line in sys.stdin:
    movie_id, rating = line.strip().split("\t")
    rating = float(rating)

    if current_movie == movie_id:
        total_rating += rating
        count += 1
    else:
        if current_movie is not None:
            avg = total_rating / count
            print(f"{current_movie}\t{avg:.2f}")
        current_movie = movie_id
        total_rating = rating
        count = 1

# 마지막 영화 출력
if current_movie is not None:
    avg = total_rating / count
    print(f"{current_movie}\t{avg:.2f}")