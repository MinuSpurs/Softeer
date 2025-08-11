# W4M1

## Dockerfile

```docker
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG SPARK_VERSION=4.0.0
ARG HADOOP_VERSION=3

ENV SPARK_VERSION=${SPARK_VERSION}
ENV HADOOP_VERSION=${HADOOP_VERSION}
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    python3 \
    python3-pip \
    net-tools \
    iputils-ping \
    ssh \
    vim

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN curl -fSL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
    rm spark.tgz

COPY scripts/ /scripts
```

- 이 Dockerfile은 Apache Spark 기반의 데이터 처리 클러스터를 위한 컨테이너 이미지를 생성
    - Java와 Spark의 HOME 경로를 설정
    - ubuntu:22.04를 사용 (python 9.0 이상 버전을 사용하기 위함)
    - 최신 Spark 버전인 4.0.0을 사용하여 java와 python 버전을 맞춰준 뒤 설치
    - 필수 패키지로 Java 17, python3, python-pip를 설치
    - 로컬에 scripts 폴더안에 있는 파일들을 **로컬** Docker 이미지의 파일 시스템에 복사

## docker-compose.yml

```yaml
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
      - ./scripts:/scripts
      - ./output:/data/output

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
      - ./scripts:/scripts
      - ./output:/data/output

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
      - ./scripts:/scripts
      - ./output:/data/output

networks:
  spark-net:
    driver: bridge
```

- 이 docker-compose.yml 파일은 Apache Spark의 Standalone 클러스터를 docker 환경에서 구성하기 위한 설정
    - spark-master
        - build: 현재 디렉토리에 있는 dockerfile로 이미지 빌드
        - container_name / hostname: 컨테이너 이름과 호스트 이름을 spark-master로 지정
        - port: 8080: 8080, 7077:7077
            - Spark Master의 Web UI 포트와 Spark Master가 작업을 받을때 사용하는 포트를 열어줌
        - command: 마스터 프로세스를 시작하고 종료되지 않도록 tail -f 사용
        - volumes: 데이터셋 입력 경로, 실행 스크립트 경로, 결과 저장 경로 설정
        
    - spark-worker-1, spark-worker-2
        - build: 마찬가지로 동일한 dockerfile을 사용해 이미지 빌드
        - depends_on: spark-master가 먼저 시작되도록 설정
        - command: Spark Master에 연결된 워커 프로세스 실행
        - volumes: 마스터와 동일한 디렉토리 마운드
        
    - 네트워크 설정
        - spark-net: 컨테이너 간 통신을 위한 사용자 정의 브리지 네트워크

## pi.py

```python
from pyspark.sql import SparkSession
import random

spark = SparkSession.builder.appName("PythonPi").getOrCreate()

partitions = 10
n = 100000 * partitions

def f(_):
    x = random.random() * 2 - 1
    y = random.random() * 2 - 1
    return 1 if x**2 + y**2 <= 1 else 0

count = spark.sparkContext.parallelize(range(n), partitions).map(f).reduce(lambda a, b: a + b)
pi = 4.0 * count / n

df = spark.createDataFrame([(pi,)], ["pi_estimate"])
df.coalesce(1).write.mode("overwrite").csv("/data/output/pi_result", header=True)

spark.stop()
```

- 이 코드는 Monte Carlo 방식으로 원주율을 추정하는 Spark application
- 실행 시 Spark 클러스터에서 병렬 작업을 수행하고 결과를 CSV 형식으로 저장
    - Application 이름은 PythonPi로 설정
- n개의 점을 10개의 파티션으로 나누어 병렬처리
- f 함수를 통해 원 안에 들어가는 점의 개수를 센다
- RDD로 병렬 처리를 한 뒤 pi 계산
    - 전체 점 중 원 안에 있는 점의 비율을 이용해 pi 추정
- 결과물은 csv 파일로 저장

## submit.sh

```bash
#!/bin/bash

/opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /scripts/pi.py \
  --output /data/output/result.csv

```

- 이 쉘 스크립트는 [pi.py](http://pi.py) 파일을 spark 클러스터에 제출하는 역할을 함
    - spark-submit: Spark 작업을 제출하는 명령어
    - —master spark://spark-master:7077: Master 노드 주소 지정
    - /scripts/pi.py: 제출할 python 스크립트 경로

## 실행

```bash
docker-compose build
```

- dockerfile과 docker-compose.yml을 build 해줌

```bash
docker-compose up -d
```

- docker compose를 실행하여 node들을 실행시켜줌
- 잘 실행됐는지 확인하기 위하여 [http://localhost:8080/](http://localhost:8080/) 로 접속하여 확인
<img width="1710" height="708" alt="image" src="https://github.com/user-attachments/assets/0e5e0801-1d1b-47ce-a347-7b4969cb326f" />

- Web UI를 통해 잘 실행된 것을 확인할 수 있음

```bash
 docker exec -it spark-master bsah
 
 bash scripts/submit.sh
```

- 이전에 작성했던 submit.sh를 실행시켜 결과를 확인
<img width="148" height="46" alt="image 1" src="https://github.com/user-attachments/assets/bd6431bf-8854-4f1c-aa96-a5d4ce4c2b18" />


- 로컬로 마운트했기 때문에 로컬에 결과 csv 파일이 생긴 것을 확인할 수 있음
