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