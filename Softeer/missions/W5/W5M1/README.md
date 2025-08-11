# W5M1

## Dockerfile

```python
# Base image
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG SPARK_VERSION=4.0.0
ARG HADOOP_VERSION=3

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64

# Install required packages
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    python3 \
    python3-pip \
    net-tools \
    iputils-ping \
    ssh \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Symlink python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Spark
RUN curl -fSL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
    rm spark.tgz

# Install Jupyter Notebook
RUN pip install notebook pyspark matplotlib pandas

# Set working directory
WORKDIR /scripts

# Copy local scripts
COPY data/ /data
```

## docker-compose.yml

```python
services:
  spark-master:
    build: .
    container_name: spark-master
    hostname: spark-master
    networks:
      - spark-net
    ports:
      - "8080:8080"
      - "7077:7077"
    command: bash -c "/opt/spark/sbin/start-master.sh && tail -f /dev/null"
    volumes:
      - ./data:/data
      - ./output:/output

  spark-worker-1:
    build: .
    container_name: spark-worker-1
    hostname: spark-worker-1
    depends_on:
      - spark-master
    networks:
      - spark-net
    command: bash -c "/opt/spark/sbin/start-worker.sh spark://spark-master:7077 && tail -f /dev/null"
    volumes:
      - ./data:/data
      - ./output:/output

  spark-worker-2:
    build: .
    container_name: spark-worker-2
    hostname: spark-worker-2
    depends_on:
      - spark-master
    networks:
      - spark-net
    command: bash -c "/opt/spark/sbin/start-worker.sh spark://spark-master:7077 && tail -f /dev/null"
    volumes:
      - ./data:/data
      - ./output:/output

  jupyter:
    build: .
    container_name: jupyter-notebook
    hostname: jupyter
    ports:
      - "8888:8888"
      - "4040:4040"
    networks:
      - spark-net
    command: bash -c "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''"
    volumes:
      - ./data:/data
      - ./output:/output

networks:
  spark-net:
    driver: bridge
```

- 이 전과 달라진건 Spark UI를 사용해야하기 때문에 4040 포트를 열어줬다.

## Jupyter Notebook

```python
from pyspark.sql import SparkSession

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("NYC TLC Trip Analysis - RDD") \
    .getOrCreate()
```

- Spark 세션을 생성해준다.
    - appName: NYC TLC Trip Analysis - RDD

```python
file_path = "/data/yellow_tripdata_2025-06.parquet"

# Parquet 파일을 DataFrame으로 읽기
df = spark.read.parquet(file_path)

# RDD로 변환
rdd = df.rdd
```

- 데이터를 불러와 DataFrame으로 읽은 뒤 RDD로 변환

```python
# 필요한 컬럼 추출: (pickup_date, fare_amount, trip_distance)
from pyspark.sql.functions import to_date

df = df.withColumn("pickup_date", to_date(df.tpep_pickup_datetime))  # 날짜만 추출

rdd = df.select("pickup_date", "fare_amount", "trip_distance").rdd.filter(lambda row: row["fare_amount"] > 0 and row["trip_distance"] > 0)
```

- 사용해줄 컬럼을 추출해준다.
    - 여기선 날짜, 요금, 거리만 추출해준다
        - 이때 거리와 요금이 0인 값을 필터링하기 위해서 lambda 조건식을 추가해준다.

```python
# 총 운행 수
total_trips = rdd.count()

# 총 수익
total_revenue = rdd.map(lambda row: row["fare_amount"]).sum()

# 평균 거리
avg_distance = rdd.map(lambda row: row["trip_distance"]).mean()

# 일별 운행 수
trips_per_day = rdd.map(lambda row: (row["pickup_date"], 1)).reduceByKey(lambda a, b: a + b).collect()

# 일별 수익
revenue_per_day = rdd.map(lambda row: (row["pickup_date"], row["fare_amount"])).reduceByKey(lambda a, b: a + b).collect()

# 실제 운행 날 수
distinct_dates = rdd.map(lambda row: row["pickup_date"]).distinct()

# 전체 RDD 에서 10%만 샘플링
sampled_rdd = rdd.sample(withReplacement=False, fraction=0.1)
```

- 각 조건에 맞는 action과 transformation을 실행해준다.
- 이 수치를 통해 Yellow cap 드라이버가 어느 정도의 수익을 버는지, 일의 강도는 어떤지 분석할 수 있다.

```python
from pyspark.sql import Row
# 모든 결과를 하나의 summary에 저장
summary = spark.createDataFrame(
    [Row(metric="total_trips", value=total_trips)] +
    [Row(metric="total_revenue", value=total_revenue)] +
    [Row(metric="avg_distance", value=avg_distance)] +
    [Row(metric=f"daily_trips_{str(k)}", value=v) for k, v in trips_per_day] +
    [Row(metric=f"daily_revenue_{str(k)}", value=v) for k, v in revenue_per_day]+
    [Row(metric="distinct_dates", value=distinct_dates)]+
    [Row(metric="sampled_rdd", value=sampled_rdd)]
)

summary.write.csv("/output/summary", header=True, mode="overwrite")
```

- CSV 형식으로 결과들을 저장해준다.

## DAG visualization

```python
total_trips = rdd.count()

total_revenue = rdd.map(lambda row: row["fare_amount"]).sum()

avg_distance = rdd.map(lambda row: row["trip_distance"]).mean()
```
<img width="228" height="576" alt="image" src="https://github.com/user-attachments/assets/e66ca68c-66a0-48c1-a97c-be7ccf0b8a4c" />


- 총 운행 수를 구할 때의 DAG 시각화이다.
    - Scan parquet: 먼저 Parquet 파일을 불러온다.
    - WholeStageCodgen (1): Spark Catalyst Optimizer가 여러 연산을 하나로 묶어 컴파일한다. 찾아보니, 이 과정은 java 내부에서 여러 연산을 수행할 수 있는 함수를 생성하여 연산 중간마다 저장하는 단계를 줄여줘 CPU 효율을 증대시킬 수 있는 역할이라고 한다.
    - map: rdd에서 필요한 컬럼만 뽑아낸 부분만 map 연산으로 처리한다.
    - mapPartitions: count()는 모든 데이터를 순회해야 하므로, 각 파티션에서 레코드 수를 세는 작업을 수행한다.
        - sum(), mean() 모두 같은 DAG를 보인다.

```python
trips_per_day = rdd.map(lambda row: (row["pickup_date"], 1)).reduceByKey(lambda a, b: a + b).collect()

revenue_per_day = rdd.map(lambda row: (row["pickup_date"], row["fare_amount"])).reduceByKey(lambda a, b: a + b).collect()
```
<img width="435" height="614" alt="image 1" src="https://github.com/user-attachments/assets/71e02719-01b9-452f-97a4-1e04e7d13820" />


- 여기서는 transformation이 일어나기 때문에, 2개의 stage로 나뉜 것을 확인할 수 있다.
    - partitionBy: key 기준으로 재분배를 해준다.
        
        ```python
        dates = rdd.map(lambda r: r["pickup_date"]).distinct().collect()
        counts = []
        for d in dates:
            c = rdd.filter(lambda r: r["pickup_date"] == d).count()
            counts.append((d, c))
        ```
        
        - shuffle이 일어난다. → 위 처럼 날짜별로 RDD를 분리한 다음 count를 세는 방법도 생각해봤으나, count 연산이 너무 오래걸릴 것 같다. 뭐가 더 나은지 조금 더 학습해봐야 할 것 같다.
    - mapPartitions: 파티션별로 reduce를 수행하여, 원하는 값을 계산해준다.
