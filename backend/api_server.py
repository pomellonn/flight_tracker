import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

BASE_DIR = Path(__file__).parent
PROCESSED_DATA = BASE_DIR / "data" / "processed"
RAW_DATA = BASE_DIR / "data" / "raw"
APP_NAME = "Flight Tracker API"

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_for_json(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
    return obj


def read_parquet(filepath: str) -> list[dict]:

    try:

        path = Path(filepath)
        if path.is_dir():
         
            parquet_files = list(path.glob("*.parquet"))
            if not parquet_files:
                return []
            df = pd.read_parquet(parquet_files[0])
        else:
            df = pd.read_parquet(filepath)
        

        records = df.to_dict(orient="records")
        

        cleaned = []
        for record in records:
            clean_record = {}
            for key, value in record.items():
                if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                    clean_record[key] = None
                elif isinstance(value, pd.Timestamp):
                    clean_record[key] = str(value)
                else:
                    clean_record[key] = value
            cleaned.append(clean_record)
        
        return cleaned
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []


@app.get("/")
def root():
    return {"message": "Flight Tracker API", "version": "1.0"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "data_dir": PROCESSED_DATA}


@app.get("/api/analytics/top-airlines")
def get_top_airlines(limit: int = 10):
    filepath = f"{PROCESSED_DATA}/top_airlines"
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="No analytics data yet. Run spark_analytics.py first.")
    
    data = read_parquet(filepath)
    return {"airlines": data[:limit]}


@app.get("/api/analytics/peak-hours")
def get_peak_hours():
    filepath = f"{PROCESSED_DATA}/peak_hours"
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="No analytics data yet.")
    
    data = read_parquet(filepath)
    return {"peak_hours": data}


@app.get("/api/analytics/countries")
def get_countries(limit: int = 20):
    filepath = f"{PROCESSED_DATA}/countries"
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="No analytics data yet.")
    
    data = read_parquet(filepath)
    return {"countries": data[:limit]}


@app.get("/api/analytics/regions")
def get_regions():
    filepath = f"{PROCESSED_DATA}/regions"
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="No analytics data yet.")
    
    data = read_parquet(filepath)
    return {"regions": data}


@app.get("/api/analytics/altitude-by-airline")
def get_altitude_by_airline(limit: int = 15):
    filepath = f"{PROCESSED_DATA}/altitude_by_airline"
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="No analytics data yet.")
    
    data = read_parquet(filepath)
    return {"airlines": data[:limit]}


@app.get("/api/analytics/summary")
def get_summary():
    summary = {}
    
    for name in ["top_airlines", "countries", "regions"]:
        filepath = f"{PROCESSED_DATA}/{name}"
        if Path(filepath).exists():
            data = read_parquet(filepath)
            summary[name] = len(data)
    
    return {"summary": summary}


@app.get("/api/flights")
def get_flights(
    min_lat: float = Query(-90, description="Minimum latitude"),
    max_lat: float = Query(90, description="Maximum latitude"),
    min_lon: float = Query(-180, description="Minimum longitude"),
    max_lon: float = Query(180, description="Maximum longitude"),
    limit: int = Query(5000, description="Max flights to return")
):
    """
    Get current flights within geographic bounds.
    Connects to: FlightMap.tsx, AircraftLayer.tsx
    """
    raw_data = RAW_DATA
    
    if not Path(raw_data).exists():
        return {"flights": [], "message": "No data yet"}
    
    try:

        parquet_files = list(Path(raw_data).rglob("*.parquet"))
        if not parquet_files:
            return {"flights": [], "message": "No parquet files found"}
        

        dfs = []
        for f in parquet_files[-10:]:
            df = pd.read_parquet(f)
            dfs.append(df)
        
        df = pd.concat(dfs, ignore_index=True)

        df = df.dropna(subset=['latitude', 'longitude'])

        # ensure stable latest-first ordering and unique aircraft
        if 'last_contact' in df.columns:
            df = df.sort_values('last_contact', ascending=False)

        if 'icao24' in df.columns:
            df = df[df['icao24'].notna()]
            df = df.drop_duplicates(subset=['icao24'], keep='first')

        filtered = df[
            (df['latitude'] >= min_lat) &
            (df['latitude'] <= max_lat) &
            (df['longitude'] >= min_lon) &
            (df['longitude'] <= max_lon)
        ]

        filtered = filtered.head(limit)

        flights = []
        for _, row in filtered.iterrows():
            flight = {
                "icao24": str(row.get('icao24', '')),
                "callsign": str(row.get('callsign', '')) if pd.notna(row.get('callsign')) else None,
                "origin_country": str(row.get('origin_country', '')) if pd.notna(row.get('origin_country')) else None,
                "latitude": float(row['latitude']) if pd.notna(row['latitude']) else None,
                "longitude": float(row['longitude']) if pd.notna(row['longitude']) else None,
                "baro_altitude": float(row['baro_altitude']) if pd.notna(row.get('baro_altitude')) else None,
                "velocity": float(row['velocity']) if pd.notna(row.get('velocity')) else None,
                "vertical_rate": float(row['vertical_rate']) if pd.notna(row.get('vertical_rate')) else None,
                "true_track": float(row['true_track']) if pd.notna(row.get('true_track')) else None,
                "on_ground": bool(row.get('on_ground', False)) if pd.notna(row.get('on_ground')) else False,
                "last_contact": int(row['last_contact']) if pd.notna(row.get('last_contact')) else None
            }
            flights.append(flight)
        
        return {"flights": flights, "count": len(flights)}
        
    except Exception as e:
        print(f"Error in /api/flights: {e}")
        return {"flights": [], "error": str(e)}


@app.get("/oskyapi/states/all")
def get_opensky_states(
    extended: int = Query(0, description="Extended format"),
    lamin: float = Query(-90, description="Min latitude"),
    lamax: float = Query(90, description="Max latitude"),
    lomin: float = Query(-180, description="Min longitude"),
    lomax: float = Query(180, description="Max longitude"),
    icao24: Optional[str] = Query(None, description="Filter by ICAO24 hex code")
):

    raw_data = RAW_DATA
    
    if not Path(raw_data).exists():
        return {"time": int(pd.Timestamp.now().timestamp()), "states": []}
    
    try:
     
        parquet_files = sorted(Path(raw_data).rglob("*.parquet"))[-5:]
        if not parquet_files:
            return {"time": int(pd.Timestamp.now().timestamp()), "states": []}
        
        dfs = [pd.read_parquet(f) for f in parquet_files]
        df = pd.concat(dfs, ignore_index=True)
        
      
        df = df.dropna(subset=['latitude', 'longitude'])
        df = df.sort_values('last_contact', ascending=False)
        df = df.drop_duplicates(subset=['icao24'], keep='first')
        

        filtered = df[
            (df['latitude'] >= lamin) &
            (df['latitude'] <= lamax) &
            (df['longitude'] >= lomin) &
            (df['longitude'] <= lomax)
        ]

        if icao24:
            filtered = filtered[
                filtered['icao24'].notna() &
                (filtered['icao24'].str.lower() == icao24.lower())
            ]
    
        timestamp = int(df['event_time'].max()) if len(df) > 0 else int(pd.Timestamp.now().timestamp())
        
        states = []
        for _, row in filtered.iterrows():
            state = [
                str(row.get('icao24', '')),
                str(row.get('callsign', '')) if pd.notna(row.get('callsign')) else None,  
                str(row.get('origin_country', '')) if pd.notna(row.get('origin_country')) else None,
                int(row['time_position']) if pd.notna(row.get('time_position')) else None,  
                int(row['last_contact']) if pd.notna(row.get('last_contact')) else None, 
                float(row['longitude']) if pd.notna(row['longitude']) else None, 
                float(row['latitude']) if pd.notna(row['latitude']) else None, 
                float(row['baro_altitude']) if pd.notna(row.get('baro_altitude')) else None, 
                bool(row.get('on_ground', False)) if pd.notna(row.get('on_ground')) else False,  
                float(row['velocity']) if pd.notna(row.get('velocity')) else None,
                float(row['true_track']) if pd.notna(row.get('true_track')) else None, 
                float(row['vertical_rate']) if pd.notna(row.get('vertical_rate')) else None,  
                float(row['geo_altitude']) if pd.notna(row.get('geo_altitude')) else None, 
                str(row.get('squawk', '')) if pd.notna(row.get('squawk')) else None,
                bool(row.get('spi', False)) if pd.notna(row.get('spi')) else False, 
                int(row.get('position_source', 0)) if pd.notna(row.get('position_source')) else 0,  
                int(row.get('category', 0)) if pd.notna(row.get('category')) else 0
                ]
            states.append(state)
        
        return {"time": timestamp, "states": states}
        
    except Exception as e:
        print(f"Error in /oskyapi/states/all: {e}")
        return {"time": int(pd.Timestamp.now().timestamp()), "states": []}


@app.get("/api/flights/latest")
def get_latest_flights(limit: int = 1000):

    raw_data = RAW_DATA
    
    if not Path(raw_data).exists():
        return {"flights": []}
    
    try:

        parquet_files = sorted(Path(raw_data).rglob("*.parquet"))[-5:]
        dfs = [pd.read_parquet(f) for f in parquet_files]
        df = pd.concat(dfs, ignore_index=True)

        if 'last_contact' in df.columns:
            df = df.sort_values('last_contact', ascending=False)

        if 'icao24' in df.columns:
            df = df.drop_duplicates(subset=['icao24'], keep='first')

        df = df.head(limit)

        records = df.to_dict(orient="records")
        for record in records:
            for key, value in list(record.items()):
                if pd.isna(value):
                    record[key] = None
        
        return {"flights": records}
    except Exception as e:
        return {"flights": [], "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


    