from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def write_result(df, output_dir: str, name: str, native_output: bool) -> None:
    if native_output:
        df.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{output_dir}/{name}")
        return

    # Windows local PySpark often lacks Hadoop native binaries. The compute still
    # runs in Spark; for the local demo we collect small mart tables and let
    # Python write CSV files without Hadoop's local FileOutputCommitter.
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df.toPandas().to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")


def run(raw_dir: str, output_dir: str, native_output: bool = False) -> None:
    spark = build_spark("distributed-bigdata-batch-etl")
    events = spark.read.option("header", True).option("inferSchema", True).csv(f"{raw_dir}/events.csv")
    items = spark.read.option("header", True).option("inferSchema", True).csv(f"{raw_dir}/items.csv")

    events = (
        events.withColumn("event_ts", F.to_timestamp("event_time"))
        .withColumn("event_date", F.to_date("event_ts"))
        .withColumn("gmv", F.when(F.col("event_type") == "purchase", F.col("quantity") * F.col("price")).otherwise(F.lit(0.0)))
    )

    counts = (
        events.groupBy("event_date")
        .pivot("event_type", ["impression", "click", "add_cart", "purchase"])
        .count()
        .na.fill(0)
    )
    base = events.groupBy("event_date").agg(
        F.countDistinct("user_id").alias("dau"),
        F.countDistinct("session_id").alias("sessions"),
        F.count("event_id").alias("events"),
        F.round(F.sum("gmv"), 2).alias("gmv"),
    )
    daily = (
        base.join(counts, "event_date", "left")
        .withColumn("ctr", F.round(F.col("click") / F.when(F.col("impression") == 0, None).otherwise(F.col("impression")), 4))
        .withColumn("cvr", F.round(F.col("purchase") / F.when(F.col("click") == 0, None).otherwise(F.col("click")), 4))
        .withColumn("arpu", F.round(F.col("gmv") / F.when(F.col("dau") == 0, None).otherwise(F.col("dau")), 4))
        .na.fill(0)
    )

    enriched = events.join(items.select("item_id", "item_name", "category"), "item_id", "left")
    purchases = enriched.where(F.col("event_type") == "purchase")
    category_sales = purchases.groupBy("event_date", "category").agg(
        F.count("event_id").alias("orders"),
        F.countDistinct("user_id").alias("buyers"),
        F.sum("quantity").alias("units"),
        F.round(F.sum("gmv"), 2).alias("gmv"),
    )
    top_items = purchases.groupBy("item_id", "item_name", "category").agg(
        F.count("event_id").alias("orders"),
        F.countDistinct("user_id").alias("buyers"),
        F.sum("quantity").alias("units"),
        F.round(F.sum("gmv"), 2).alias("gmv"),
    ).orderBy(F.desc("gmv")).limit(100)

    write_result(daily, output_dir, "daily_overview", native_output)
    write_result(category_sales, output_dir, "category_sales", native_output)
    write_result(top_items, output_dir, "top_items", native_output)
    spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Spark batch ETL.")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output-dir", default="warehouse/spark_marts")
    parser.add_argument(
        "--native-output",
        action="store_true",
        help="Use Spark's native CSV writer. Recommended in Linux/K8s clusters; Windows local demo uses driver-side CSV export by default.",
    )
    args = parser.parse_args()
    run(args.raw_dir, args.output_dir, native_output=args.native_output)


if __name__ == "__main__":
    main()
