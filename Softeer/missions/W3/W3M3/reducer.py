#!/usr/bin/env python3
import sys

current = None
count = 0

for line in sys.stdin:
    word, c = line.rstrip("\n").split("\t", 1)
    c = int(c)
    if current == word:
        count += c
    else:
        if current is not None:
            print(f"{current}\t{count}")
        current = word
        count = c

if current is not None:
    print(f"{current}\t{count}")