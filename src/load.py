import argparse
from pyspark.sql import SparkSession, functions as F
import os

parser = argparse.ArgumentParser()
parser.add_argument("--start_date", type=str, help="Data inicial (YYYY-MM-DD)")
parser.add_argument("--end_date", type=str, help="Data final (YYYY-MM-DD)")
args = parser.parse_args()
dt_start = args.start_date
dt_end = args.end_date

spark = SparkSession.builder.appName("silver_to_gold").getOrCreate()
silver_path = os.getenv("SILVER_PATH", "/data/silver/breweries/")
gold_path = os.getenv("GOLD_PATH", "/data/gold/breweries_agg/")

df = spark.read.parquet(silver_path)

if "dt" in df.columns and dt_start and dt_end:
    df = df.filter((F.col("dt") >= dt_start) & (F.col("dt") <= dt_end))
    print(f"[load.py] Agregando para o range {dt_start} a {dt_end}")

if "state" not in df.columns:
    raise Exception("Coluna 'state' não encontrada no dataframe!")
if "brewery_type" not in df.columns:
    raise Exception("Coluna 'brewery_type' não encontrada no dataframe!")

agg = (
    df.groupBy("state", "brewery_type")
      .agg(
        F.count("*").alias("brewery_count"),
        F.collect_set("dt").alias("dates")
      )
      .withColumn("agg_ts", F.current_timestamp())
)

agg.write.mode("overwrite").partitionBy("state").parquet(gold_path)
print(f"[load.py] Gold criado em {gold_path} com {agg.count()} linhas")
agg.show(5, truncate=False)
