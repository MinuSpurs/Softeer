# W3M5

## Mapper.py

```python
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
```

- 헤더를 건너뛰고 입력 파일(rating.csv) 한 줄씩 읽음
- 각 줄에서 movieId와 rating을 추출하여 출력 (movieId<TAB>rating 형식)

## Reduce.py

```python
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
```

- Mapper에서 넘겨준 movieId\t 평점 데이터들을 영화별로 그룹화
- 각 영화에 대해 평균 평점 계산 후 출력

## 데이터 hdfs로 전송

```python
docker cp /Users/minwoo/Desktop/softeer/data_engineering_course_materials/missions/W3/W3M5/ml-20m/ratings.csv namenode:/ratings.csv

docker cp mapper.py namenode:/mapper.py 

docker cp reducer.py namenode:/reducer.py
```

- namenode와 worker node를 실행시켜 준 뒤 docker cp를 통해 namenode로 전송

## HDFS에서 Mapreduce job 실행

```python
chmod +x /mapper.py /reducer.py # root에서 실행

hdfs dfs -mkdir -p /input

hdfs dfs -put -f /ratings.csv /input/

hadoop jar \$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
     -D mapreduce.job.reduces=1 \
     -files /mapper.py,/reducer.py \
     -mapper \"python3 mapper.py\" \
     -reducer \"python3 reducer.py\" \
     -input /input/ratings.csv \
     -output /output/movie_avg_ratings
```

- root 계정에서 파이썬 파일의 권한을 hadoop 에서도 사용할 수 있게 풀어줌
- input 폴더를 만든 뒤에 ratings.csv를 만듦
- Mapreduce job 결과는 output 폴더를 만들어 저장

## 결과 확인

```python
hdfs dfs -cat /output/movie_avg_ratings/part-00000 | head -20

1	3.92
10	3.43
100	3.22
1000	3.11
100003	3.67
100006	2.50
100008	3.42
100010	2.80
100013	3.20
100015	2.00
100017	3.10
100032	3.42
100034	3.15
100036	3.05
100038	3.42
100040	3.00
100042	3.33
100044	3.80
100046	3.12
100048	3.00
```

- 20개만 결과 확인

```python
hdfs dfs -cat /output/movie_avg_ratings/part-00000 | sort -t$'\t' -k2 -nr | head -20

99450	5.00
99243	5.00
98761	5.00
95979	5.00
95977	5.00
95517	5.00
94972	5.00
94949	5.00
94737	5.00
94657	5.00
94431	5.00
93967	5.00
93707	5.00
92956	5.00
92783	5.00
89133	5.00
88488	5.00
86055	5.00
81117	5.00
79866	5.00
```

- 평점 상위 20개 결과 확인