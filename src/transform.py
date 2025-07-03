import argparse
from datetime import datetime
from src.utils import daterange

from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, regexp_extract, col, lower, trim, when, current_timestamp

parser = argparse.ArgumentParser()
parser.add_argument("--start_date", type=str, help="Data inicial (YYYY-MM-DD)")
parser.add_argument("--end_date", type=str, help="Data final (YYYY-MM-DD)")
args = parser.parse_args()

bronze_path = "/data/bronze/breweries"
silver_path = "/data/silver/breweries"

if args.start_date and args.end_date:
    start_dt = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    dates = [d.strftime("%Y-%m-%d") for d in daterange(start_dt, end_dt)]
    input_paths = [f"{bronze_path}/state=*/dt={dt}/*.json" for dt in dates]
    print(f"[transform.py] Lendo dados de {args.start_date} até {args.end_date}")
else:
    input_paths = [f"{bronze_path}/state=*/dt=*/"]
    print("[transform.py] Lendo todos os dados disponíveis.")

spark = SparkSession.builder.getOrCreate()
df = spark.read.json(input_paths)

if 'dt' not in df.columns:
    df = df.withColumn(
        "dt",
        regexp_extract(input_file_name(), r"dt=(\d{4}-\d{2}-\d{2})", 1)
    )

if 'state' not in df.columns and 'state_province' in df.columns:
    df = df.withColumnRenamed("state_province", "state")

if 'state' in df.columns:
    df = df.withColumn("state", when(col("state").isNull(), "unknown").otherwise(trim(lower(col("state")))))

df = df.withColumn("ingestion_ts", current_timestamp())
df = df.dropDuplicates(["id", "dt"])
df.write.mode("overwrite").partitionBy("state", "dt").parquet(silver_path)

print(f"[transform.py] Total registros após tratamento: {df.count()}")
df.printSchema()
df.show(5)
