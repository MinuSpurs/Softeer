# W5M2

```python
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, to_date
from pyspark import StorageLevel

spark = (
    SparkSession.builder
    .appName("W5M2-NYC-Taxi-Weather-RDD")
    .getOrCreate()
)
```

- 필요한 라이브러리들과 Spark를 실행시켜 준다.

```python
# trip 데이터 로드 및 전처리
trip_df = (
    spark.read.parquet("/data/yellow_tripdata_2024-01.parquet")
    .withColumn("pickup_date", to_date("tpep_pickup_datetime"))        # 날짜 컬럼 생성
    .filter((col("fare_amount") > 0) & (col("trip_distance") > 0))     # 이상치 제거
)

# DF -> RDD 변환
trip_rdd = (
    trip_df
    .select("pickup_date", "fare_amount")   # 집계에 필요한 두 컬럼만
    .rdd
    .map(lambda r: (r["pickup_date"], (1, r["fare_amount"])))          # (date,(1, fare))
    .persist(StorageLevel.MEMORY_AND_DISK)
)
_ = trip_rdd.count()        # Action을 통해 캐시를 메모리에 확정적으로 올림

# 한 번의 reduceByKey 로 일별 운행 수와 수익 동시 집계
agg_rdd = trip_rdd.reduceByKey(
    lambda a, b: (a[0] + b[0], a[1] + b[1])
)
```

- 두개의 stage를 갖지 않게 하기 위하여, 운행 수와 수익을 한번의 reduceByKey로 계산해 lineage를 하나로 유지했다.
- Action을 해주지 않으면 메모리에 올라가지 않기 때문에 count를 통해서 메모리에 올려준다.
    - 코드상 trip_rdd.persist() 뒤에 Action( count() ) 을 넣어야 캐시가 실제로 메모리에 올라간다. → Lazy evaluation
- 각각 다르게 계산을 해주면 Scan parquet이 두번 일어나, stage가 하나 더 나오게 된다.

```python
# 날씨 데이터 로드 및 RDD 변환
weather_rdd = (
    spark.read.option("header", True)
        .csv("/data/NYC_weather.csv", inferSchema=True)
        .withColumn("weather_date", to_date("datetime"))
        .select("weather_date", "temp")
        .rdd
        .map(lambda r: (r["weather_date"], r["temp"]))
)
# 날짜 기준 Joi
joined = agg_rdd.join(weather_rdd)
```

- Join을 수행해 줄 날씨 데이터 로드 해준 뒤 RDD로 변환

```python
result_df = (
    joined
    .map(lambda x: Row(
        date=str(x[0]),
        total_trips=x[1][0][0],
        total_revenue=x[1][0][1],
        avg_temperature=x[1][1]
    ))
    .toDF()
)

result_df.write.mode("overwrite")\
        .csv("/output/rdd_weather_summary", header=True)
```

- 최종 Row로 변환 및 저장
    - 전체 운행 수, 전체 수익, 평균 온도를 저장해준다.

```python
summary_df = spark.createDataFrame(
    [
        Row(metric="total_trips", value=float(result_df.agg({"total_trips": "sum"}).first()[0])),
        Row(metric="total_revenue", value=float(result_df.agg({"total_revenue": "sum"}).first()[0])),
        Row(metric="avg_distance", value=float(
            trip_df.select("trip_distance").agg({"trip_distance": "avg"}).first()[0]
        )),
    ]
)
summary_df.write.mode("overwrite")\
        .csv("/output/rdd_summary", header=True)
```

- 날짜별로 각 수치(전체 운행 수, 전체 수익, 평균 온도)를 저장해준다.

## DAG visualization

![image.png](W5M2%2024672994258d801baaf6ffa1b65334ab/image.png)

- Stage 4 - Parquet 파일 로딩 및 캐싱
    
    ```python
    trip_df = spark.read.parquet("/data/yellow_tripdata_2024-01.parquet") \
        .withColumn("pickup_date", to_date("tpep_pickup_datetime")) \
        .filter((col("fare_amount") > 0) & (col("trip_distance") > 0))
    
    trip_rdd = trip_df.select("pickup_date", "fare_amount", "trip_distance") \
        .rdd.map(lambda r: (r["pickup_date"], (1, r["fare_amount"]))) \
        .persist(StorageLevel.MEMORY_AND_DISK)
    
    trip_rdd.count()  
    ```
    
    - 이 스테이지에서는 parquet 파일이 한 번만 스캔된다.
    - 그 후 .map()과 ,mapPartitions()등을 통해 RDD로 변환한 뒤 원하는 형태로 데이터를 변환해준다.
    - 녹색 점은 .count()로 캐시가 실제로 메모리에 올라간 것을 의미한다.
    - 이 스테이지 이후부터 trip_rdd를 재사용하게 설계하여 다시 scan parquet이 일어나 새로운 stage를 만드는 것을 방지한다.

- Stage 6 - 날짜 기준 집계
    
    ```python
    agg_rdd = trip_rdd.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
    ```
    
    - reduceByKey는 groupByKey를 포함하는 transformation이므로 shuffle이 발생하고 새로운 스테이지가 만들어 진다.

- Stage 5 - CSV 날씨 데이터 로딩 + Join + 저장

```python
weather_rdd = spark.read.option("header", True).csv("/data/NYC_weather.csv", inferSchema=True) \
    .withColumn("weather_date", to_date("datetime")) \
    .select("weather_date", "temp") \
    .rdd.map(lambda r: (r["weather_date"], r["temp"]))

joined = agg_rdd.join(weather_rdd)

result_df = joined.map(lambda x: Row(
    date=str(x[0]),
    total_trips=x[1][0],
    total_revenue=x[1][1],
    avg_temperature=x[1][2]
)).toDF()

result_df.write.mode("overwrite").csv("/output/rdd_weather_summary", header=True)
```

- 여기서 Scan csv가 일어나고 RDD로 변한된다.
- 그 다음 .join()을 통해 날짜 기준으로 trip 집계와 weather 데이터를 join하여 DAG 상에 연결선으로 표현된다.
- 마지막으로 .write.csv()를 통해 최종 action을 실행해준다.