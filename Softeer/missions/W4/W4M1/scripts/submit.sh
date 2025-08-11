#!/bin/bash

/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /scripts/pi.py \
  --output /data/output/result.csv
