#!/usr/bin/env python3
import sys, re

word_re = re.compile(r"[A-Za-z']+")  # 단어만 추출(간단 정규식)
for line in sys.stdin:
    for w in word_re.findall(line.lower()):
        print(f"{w}\t1")