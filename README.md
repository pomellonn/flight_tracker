# Flight tracker

A Big Data flight tracking and analytics system that collects live flight data from the OpenSky Network API, processes it with Apache Spark, and visualizes it on an interactive Mapbox map via a React frontend.

---

## Overview

The system ingests ~8,000 live flights every 60 seconds, stores them as compressed Parquet snapshots, runs batch analytics with PySpark, and serves everything through a FastAPI backend to a React + Mapbox frontend.

**Highlights:**
- ~1.9 million flight records across 243 Parquet snapshots
- Airline rankings, peak traffic hours, geographic distribution, and altitude patterns
- OpenSky-compatible REST API — minimal frontend changes required
- Full-stack: Python data pipeline → FastAPI → React + Mapbox GL

---

## Architecture

```
OpenSky API  →  ingestor.py  →  ./data/raw/ (Parquet)
                                      ↓
                          spark_analytics.py (PySpark)
                                      ↓
                          ./data/processed/ (aggregations)
                                      ↓
                            api_server.py (FastAPI)
                                      ↓
                          React + Mapbox GL (frontend)
```

### Data Flow

1. **Ingestion** — `ingestor.py` polls the OpenSky API every 60 s with retry/backoff logic and writes Parquet files partitioned by `year/month/day`.
2. **Storage** — Snappy-compressed Parquet files in `./data/raw/`.
3. **Processing** — `spark_analytics.py` reads raw data and writes aggregated results to `./data/processed/`.
4. **Serving** — `api_server.py` reads the latest Parquet snapshots and exposes REST endpoints.
5. **Visualization** — React frontend renders live aircraft markers on an interactive Mapbox map.

---

## Technology Stack

| Component | Technology | Version |
|---|---|---|
| Data Processing | Apache Spark (PySpark) | 3.5.3 |
| Storage Format | Parquet (Snappy compression) | — |
| Data Manipulation | Pandas | 2.2.3 |
| API Framework | FastAPI | 0.115.6 |
| Frontend | React + TypeScript | 19.1.0 |
| Build Tool | Vite | 7.0.0 |
| Map Visualization | Mapbox GL | 3.13.0 |
| HTTP Client | Requests | 2.32.3 |

---


## Getting Started


### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Step 1: Start data collection (runs continuously)
python3 backend/ingestor.py

# Step 2: Run Spark analytics (once enough data is collected)
python3 backend/spark_analytics.py

# Step 3: Start the API server
python3 backend/api_server.py
```

### Frontend Setup

```bash
# Install Node dependencies
npm install

# Add your Mapbox token
echo "VITE_REACT_MAPBOX_TOKEN=pk.your_token_here" > .env.local

# Start the development server
npm run dev
```

### Access Points

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Documentation | http://localhost:8000/docs |

---

## Analytics

Running `spark_analytics.py` generates the following outputs in `./data/processed/`:

| Output | Description |
|---|---|
| `top_airlines/` | Top 10 airlines by flight count with avg. altitude & speed |
| `peak_hours/` | Hourly flight distribution by country |
| `countries/` | Total flight counts per origin country |
| `regions/` | Geographic distribution (Europe, North America, Asia, etc.) |
| `altitude_by_airline/` | Avg. altitude statistics per airline |
| `speed_distribution/` | Aircraft speed categorization |
| `anomalies/` | Unusual flight pattern detection |







*Beijing Institute of Technology — Big Data Processing Technology, April 2026*
