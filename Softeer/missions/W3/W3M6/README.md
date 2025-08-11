# W3M6

- 이번 미션에서 사용한 데이터는 **Handmade_Products**
    - https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Handmade_Products.jsonl.gz

## amazon_mapper.py

```python
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
        continue 
```

- HDFS에 있는 .jsonl 리뷰 데이터에서 제품 ID (asin)와 평점 (rating)만 추출해 출력
    
    → product_id<TAB>rating 형태로 출력
    

## amazon_reducer.py

```python
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
```

- 동일한 product_id에 대해 평점을 누적하여 총 리뷰 수와 평균 평점을 계산함
    
    → product_id<TAB>리뷰 수<TAB>평균 평점 출력
    

## 데이터 hdfs로 전송

```python
docker cp Handmade_Products.jsonl namenode:/Handmade_Products.jsonl

docker cp amazon_mapper.py namenode:/amazon_mapper.py 

docker cp amazon_reducer.py namenode:/amazon_reducer.py
```

- namenode와 worker node를 실행시켜 준 뒤 docker cp를 통해 namenode로 전송

## HDFS에서 Mapreduce job 실행

```python
chmod +x /amazon_mapper.py /amazon_reducer.py # root에서 실행

hdfs dfs -mkdir -p /input

hdfs dfs -put -f /Handmade_Products.jsonl /input/

hadoop jar \$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
     -D mapreduce.job.reduces=1 \
     -files /amazon_mapper.py,/amazon_reducer.py \
     -mapper \"python3 amazon_mapper.py\" \
     -reducer \"python3 amazon_reducer.py\" \
     -input /input/Handmade_Products.jsonl \
     -output /output/amazon_avg_ratings
```

- root 계정에서 파이썬 파일의 권한을 hadoop 에서도 사용할 수 있게 풀어줌
- input 폴더를 만든 뒤에 Handmade_Products.jsonl를 저장
- Mapreduce job 결과는 output 폴더를 만들어 저장

## 결과

- 단순 20개 조회

```python
hdfs dfs -cat /output/amazon_avg_ratings/part-00000 | head -20

B0003TOQIK	1	5.00
B0003TOR7U	3	5.00
B0003YDVOU	6	4.17
B000406CNA	2	5.00
B000406HCG	1	5.00
B0004K4BO2	1	4.00
B0004K4D40	10	4.20
B0004K4FCA	2	5.00
B0004K4JXA	4	5.00
B0004K4KSE	2	4.00
B0004K4LMY	1	5.00
B0004K4LZG	5	4.80
B0004K4MSC	7	5.00
B0004K4NNQ	1	5.00
B0004K4TCQ	3	5.00
B0004K4UGQ	1	5.00
B0004K4WFA	5	4.20
B0004K4YNK	2	5.00
B0004K52OK	5	4.40
B0004K55EM	1	5.00
```

- 리뷰수 순 상위 20개 정렬

```python
hdfs dfs -cat /output/amazon_avg_ratings/part-00000 | sort -t$'\t' -k2 -nr | head -20

B07RC9FWLN	1305	4.92
B01G29HQ8G	1088	4.56
B01ASDYQQC	1044	4.92
B01N5SVHUU	972	3.55
B083Q2N1KQ	913	3.85
B07NP52Y1F	896	4.29
B015NSJ11W	887	3.45
B081732LNJ	766	4.79
B015HVACEA	734	4.30
B077J2BF57	699	4.95
B07BSJG8F5	672	4.96
B0779MS18Z	669	4.63
B096G34R6P	649	4.57
B01B6DF5WW	598	4.81
B015YI5I40	592	4.50
B07D645HM4	589	4.56
B07H5T2QH6	569	4.84
B07WZ5DYCC	530	4.18
B07NTVVY36	530	3.95
B077CWRBQZ	502	3.71
```

- 평점 순 20개 정렬

```python
hdfs dfs -cat /output/amazon_avg_ratings/part-00000 | sort -t$'\t' -k3,3nr | head -20

B0003TOQIK	1	5.00
B0003TOR7U	3	5.00
B000406CNA	2	5.00
B000406HCG	1	5.00
B0004K4FCA	2	5.00
B0004K4JXA	4	5.00
B0004K4LMY	1	5.00
B0004K4MSC	7	5.00
B0004K4NNQ	1	5.00
B0004K4TCQ	3	5.00
B0004K4UGQ	1	5.00
B0004K4YNK	2	5.00
B0004K55EM	1	5.00
B000F7AAA8	1	5.00
B000PGKQW6	2	5.00
B001KVUW42	6	5.00
B001KVWYXO	1	5.00
B001KVWZO2	2	5.00
B001KW13NU	1	5.00
B001KW517Y	1	5.00
```