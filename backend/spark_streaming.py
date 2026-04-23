import os
import time
import requests
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType


OPENSKY_API = "https://opensky-network.org/api/states/all"
OPENSKY_TOKEN = os.getenv("OPENSKY_TOKEN", "")
BATCH_INTERVAL = 10
APP_NAME = "FlightTrackerStreaming"


def create_spark_streaming_session():
    return SparkSession.builder.appName(APP_NAME).config("spark.sql.adaptive.enabled", "true").config("spark.driver.memory", "2g").getOrCreate()


def fetch_flights_batch():
    headers = {}
    if OPENSKY_TOKEN:
        headers["Authorization"] = f"Bearer {OPENSKY_TOKEN}"
    
    try:
        response = requests.get(OPENSKY_API, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        states = data.get("states", [])
        timestamp = data.get("time", int(time.time()))
        seen = set()
        
        flights = []
        for state in states:
            if not state or len(state) < 17:
                continue

            icao = state[0]
            if icao in seen:
                continue
            seen.add(icao)
            
            if state[5] is None or state[6] is None:
                continue
            
            flights.append({
                "event_time": timestamp,
                "icao24": state[0],
                "callsign": state[1].strip() if isinstance(state[1], str) else None,
                "origin_country": state[2],
                "longitude": state[5],
                "latitude": state[6],
                "baro_altitude": state[7] if state[7] else 0,
                "velocity": state[9] if state[9] else 0,
                "on_ground": bool(state[8]) if state[8] is not None else False
            })
        
        return flights
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def process_stream(spark: SparkSession, batch_interval: int):

    schema = StructType([
        StructField("event_time", LongType(), True),
        StructField("icao24", StringType(), True),
        StructField("callsign", StringType(), True),
        StructField("origin_country", StringType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("baro_altitude", DoubleType(), True),
        StructField("velocity", DoubleType(), True),
        StructField("on_ground", StringType(), True),
    ])

    
    while True:
        try:
            flights = fetch_flights_batch()
            
            if flights:
                df = spark.createDataFrame(flights, schema)
       
                by_country = df.groupBy("origin_country") \
                    .agg(F.count("*").alias("count")) \
                    .orderBy(F.col("count").desc()) \
                    .limit(5)
                
                print("Top 5 countries:")
                by_country.show(truncate=False)
                

                avg_alt = df.select(F.avg("baro_altitude")).first()[0]
                if avg_alt is not None:
                    print(f"Average altitude: {avg_alt:.0f}m")
                else:
                    print("Average altitude: N/A")
            
                avg_vel = df.select(F.avg("velocity")).first()[0]
                if avg_vel is not None:
                    print(f"Average velocity: {avg_vel:.0f} m/s")
                else:
                    print("Average velocity: N/A")
                
                airborne = df.filter(F.col("on_ground") == "false").count()
                ground = df.filter(F.col("on_ground") == "true").count()
                print(f"Airborne: {airborne}, On ground: {ground}")
                
                top_airlines = df.filter(F.col("callsign").isNotNull()).withColumn("airline", F.substring(F.col("callsign"), 1, 3)) \
                    .groupBy("airline").agg(F.count("*").alias("count")).orderBy(F.col("count").desc()).limit(5)
                
                print("Top 5 airlines:")
                top_airlines.show(truncate=False)
                

            
            time.sleep(batch_interval)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in stream: {e}")
            time.sleep(batch_interval)


def run_streaming():
    spark = create_spark_streaming_session()
    process_stream(spark, BATCH_INTERVAL)
    spark.stop()


if __name__ == "__main__":
    run_streaming()