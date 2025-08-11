# W3M4

## mapper.py

```python
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
```

- CSV 파일의 각 트윗 텍스트를 읽고, TextBlob을 이용해 감정(positive/neutral/negative)을 분류한 후 <감정>\t1 형태로 출력
- TextBlob의 sentiment.polarity 값은 -1.0(매우 부정) ~ 1.0(매우 긍정)
- 입력으로 들어온 CSV 라인을 처리하고, 트윗만 추출해 감정 분류
- 감정 카테고리를 key, 1을 value로 출력

## reducer.py

```python
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
```

- mapper.py의 출력값을 입력으로 받아 감정별로 개수를 집계
- 같은 감정 키가 연속으로 들어온다고 가정하고 누적합 계산
- 감정이 바뀔 때마다 지금까지의 감정 개수 출력

## HDFS로 데이터 이동

```python
docker cp reducer.py namenode:/home/hadoop/ 
docker cp mapper.py namenode:/home/hadoop/   
docker cp tweet_labeled.csv namenode:/home/hadoop/ 
```

- docker cp 명령어를 통해 hdfs로 mapper.py, reducer.py, tweet_labeled.csv를 전송

```python
chmod +x /home/hadoop/mapper.py
chmod +x /home/hadoop/reducer.py
```

- chmod로 실행시킬 파이썬 파일의 권한을 풀어줌

```python
hdfs dfs -put /home/hadoop/reducer.py /input
hdfs dfs -put /home/hadoop/mapper.py /input
hdfs dfs -put /home/hadoop/tweet_labeled.csv /input
```

- hadoop 폴더에 있는 코드를 실행시키기 위하여 input 폴더로 옮겨줌

## 라이브러리 다운로드

```python
pip install -U textblob
python3 -m textblob.download_corpora
```

- mapper.py에서 사용한 textblob 라이브러리를 사용하기 위해 namenode, worker1, worker2에 라이브러리를 설치해주고 필요한 corpus로 설치해줌

## Mapreduce job

```python
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
   -input /input/tweet_labeled.csv \
   -output /output/tweet_sentiment_output \
   -mapper /home/hadoop/mapper.py \
   -reducer /home/hadoop/reducer.py \
   -file /home/hadoop/mapper.py \
   -file /home/hadoop/reducer.py
```

- Mapreduce job을 실행시켜줌

```python
hdfs dfs -ls /output/tweet_sentiment_output

Found 2 items
-rw-r--r--   2 hadoop supergroup          0 2025-07-24 09:54 /output/tweet_sentiment_output/_SUCCESS
-rw-r--r--   2 hadoop supergroup         47 2025-07-24 09:54 /output/tweet_sentiment_output/part-00000
```

```python
cat tweet_result/part-00000

negative	270697
neutral	709671
positive	619633
```

- 결과가 잘 저장된 것을 확인한 후에 결과를 확인해봄