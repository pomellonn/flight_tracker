from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
    LongType,
    BooleanType,
)
from pathlib import Path

DATA_INPUT = "./data/raw"
DATA_OUTPUT = "./data/processed"
APP_NAME = "FlightTrackerAnalytics"


def create_spark_session():
    return (
        SparkSession.builder.appName(APP_NAME)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def load_flight_data(spark: SparkSession, path: str):

    df = spark.read.parquet(path)
    df = df.withColumn("hour", F.from_unixtime("event_time", "HH")) \
           .withColumn("date", F.to_date(F.from_unixtime("event_time")))
    
    return df

def analytics_top_airlines(df):
    print("TOP 10 BUSIEST AIRLINES\n")

    airline_df = df.filter(
        F.col("callsign").isNotNull() & (F.length(F.col("callsign")) >= 3)
    ).withColumn(
        "airline", F.substring(F.col("callsign"), 1, 3)
    )

    result = (
        airline_df.groupBy("airline", "origin_country")
        .agg(
            F.count("*").alias("flight_count"),
            F.avg("baro_altitude").alias("avg_altitude"),
            F.avg("velocity").alias("avg_velocity"),
            F.max("baro_altitude").alias("max_altitude"),
        )
        .orderBy(F.col("flight_count").desc())
        .limit(10)
    )

    result.show(truncate=False)

    result.coalesce(1).write.mode("overwrite").parquet(f"{DATA_OUTPUT}/top_airlines")
    return result


def analytics_peak_hours(df):
    print("PEAK HOURS OF AIR TRAFFIC\n")
    hourly_df = df

    result = (
        hourly_df.groupBy("hour", "origin_country")
        .agg(
            F.count("*").alias("flight_count"),
            F.avg("baro_altitude").alias("avg_altitude"),
        )
        .orderBy("origin_country", "hour")
    )

    result.show(20, truncate=False)

    result.coalesce(1).write.mode("overwrite").parquet(f"{DATA_OUTPUT}/peak_hours")
    return result


def analytics_altitude_by_airline(df):
    print("AVERAGE ALTITUDE BY AIRLINE")

    airline_df = df.filter(F.col("callsign").isNotNull()).withColumn(
        "airline", F.substring(F.col("callsign"), 1, 3)
    )

    result = (
        airline_df.groupBy("airline")
        .agg(
            F.count("*").alias("total_flights"),
            F.avg("baro_altitude").alias("avg_altitude"),
            F.stddev("baro_altitude").alias("altitude_stddev"),
            F.min("baro_altitude").alias("min_altitude"),
            F.max("baro_altitude").alias("max_altitude"),
        )
        .filter(F.col("total_flights") > 10)
        .orderBy(F.col("avg_altitude").desc())
    )

    result.show(15, truncate=False)

    result.coalesce(1).write.mode("overwrite").parquet(
        f"{DATA_OUTPUT}/altitude_by_airline"
    )
    return result


def analytics_countries(df):
    print("COUNTRIES WITH MOST FLIGHTS\n")

    result = (
        df.groupBy("origin_country")
        .agg(
            F.count("*").alias("total_flights"),
            F.countDistinct("icao24").alias("unique_aircraft"),
            F.avg("baro_altitude").alias("avg_altitude"),
            F.avg("velocity").alias("avg_velocity"),
        )
        .orderBy(F.col("total_flights").desc())
    )

    result.show(20, truncate=False)

    result.coalesce(1).write.mode("overwrite").parquet(f"{DATA_OUTPUT}/countries")
    return result


def analytics_regions(df):
    print("FLIGHTS BY REGION\n")

    region_df = df.withColumn(
        "region",
        F.when(
            (F.col("latitude") >= 30)
            & (F.col("latitude") <= 60)
            & (F.col("longitude") >= -10)
            & (F.col("longitude") <= 40),
            "Europe",
        )
        .when(
            (F.col("latitude") >= 25)
            & (F.col("latitude") <= 50)
            & (F.col("longitude") >= -130)
            & (F.col("longitude") <= -65),
            "North America",
        )
        .when(
            (F.col("latitude") >= -40)
            & (F.col("latitude") <= -10)
            & (F.col("longitude") >= 100)
            & (F.col("longitude") <= 180),
            "Asia Pacific",
        )
        .otherwise("Other"),
    )

    result = (
        region_df.groupBy("region")
        .agg(
            F.count("*").alias("flight_count"),
            F.avg("baro_altitude").alias("avg_altitude"),
            F.avg("velocity").alias("avg_velocity"),
        )
        .orderBy(F.col("flight_count").desc())
    )

    result.show(truncate=False)

    result.coalesce(1).write.mode("overwrite").parquet(f"{DATA_OUTPUT}/regions")
    return result


def run_analytics():
    spark = create_spark_session()

    try:
        df = load_flight_data(spark, DATA_INPUT)

        df = df.dropna(subset=["latitude", "longitude", "icao24"])
        df = df.dropDuplicates(["icao24"])
        df = df.orderBy(F.col("event_time").desc())

        df.cache()
        print(f"Loaded {df.count()} flight records")

        analytics_top_airlines(df)
        analytics_peak_hours(df)
        analytics_altitude_by_airline(df)
        analytics_countries(df)
        analytics_regions(df)

    finally:
        spark.stop()


if __name__ == "__main__":
    run_analytics()
