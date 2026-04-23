import os
import time
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

OPENSKY_API = "https://opensky-network.org/api/states/all"
DATA_DIR = Path("./data/raw")
POLL_INTERVAL = 60 
OPENSKY_TOKEN = os.getenv("OPENSKY_TOKEN", "") 
REQUEST_TIMEOUT = 60 
MAX_RETRIES = 3
RETRY_DELAY = 5

DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_flights() -> list[dict]:
    """Fetch current flight states from OpenSky API with retry logic."""
    headers = {}
    if OPENSKY_TOKEN:
        headers["Authorization"] = f"Bearer {OPENSKY_TOKEN}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(OPENSKY_API, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            break 
        except (requests.RequestException, requests.Timeout) as e:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt) 
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"All {MAX_RETRIES} attempts failed")
                return []
    
    states = data.get("states", [])
    timestamp = data.get("time", int(datetime.now().timestamp()))
    
    print(f"API returned {len(states) if states else 0} state vectors at time {timestamp}")
    
    if not states:
        return []
    seen = set()
    
    flights = []
    for state in states:
        icao = state[0]
        if icao in seen:
            continue
        seen.add(icao)
        if len(flights) == 0 and len(state) > 0:
            print(f"First state sample: {state[:5]}...")
        
        if len(state) < 6:
            continue
            
        if state[5] is None or state[6] is None:
            continue
                
        if len(state) < 17:
            continue
        
        flight = {
            "event_time": timestamp,
            "ingest_time": timestamp,
            "icao24": state[0],
            "callsign": state[1].strip() if isinstance(state[1], str) else None,
            "origin_country": state[2],
            "time_position": state[3],
            "last_contact": state[4],
            "longitude": state[5],
            "latitude": state[6],
            "baro_altitude": state[7],
            "on_ground": state[8],
            "velocity": state[9],
            "true_track": state[10],
            "vertical_rate": state[11],
            "sensors": state[12] if len(state) > 12 else None,
            "geo_altitude": state[13] if len(state) > 13 else None,
            "squawk": state[14] if len(state) > 14 else None,
            "spi": state[15] if len(state) > 15 else False,
            "position_source": state[16] if len(state) > 16 else 0,
            "category": state[17] if len(state) > 17 else 0
        }
        flights.append(flight)
    
    if not flights:
        print("No valid flight data returned from OpenSky")
        return []
    print(f"Processed {len(flights)} flights with valid coordinates")
    return flights
        


def save_to_parquet(flights: list[dict]):
    if not flights:
        return
    
    df = pd.DataFrame(flights)
    now = datetime.now()
    filename = f"flights_{now.strftime('%Y%m%d_%H%M')}.parquet"

    partition_path = DATA_DIR / f"year={now.year}" / f"month={now.month:02d}" / f"day={now.day:02d}"
    partition_path.mkdir(parents=True, exist_ok=True)
    
    filepath = partition_path / filename
    df.to_parquet(filepath, engine="pyarrow", compression="snappy")

def run_ingestor():

    while True:
        flights = fetch_flights()
        if flights:
            save_to_parquet(flights)
        else:
            print("no flights fetched, skipping save")
        
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_ingestor()
