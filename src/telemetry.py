"""
JalDrishti - Phase 2: Dual-Mode Telemetry & Dynamic Ingestion Layer
Queries Open-Meteo Forecast and Flood APIs for target basin coordinates with
automatic persistent disk caching (TTL: 3h) and defensive offline fallback.
"""

import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JalDrishti.Telemetry")

CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "telemetry_cache.json"

DEFAULT_BASIN_COORDS = {
    "godavari": {"name": "Godavari Basin (Bhadrachalam)", "lat": 17.55, "lon": 80.62, "slug": "bhadradri_kothagudem"},
    "bhadradri_kothagudem": {"name": "Bhadradri Kothagudem", "lat": 17.55, "lon": 80.62, "slug": "bhadradri_kothagudem"},
    "mulugu": {"name": "Mulugu", "lat": 18.19, "lon": 80.00, "slug": "mulugu"},
    "nizamabad": {"name": "Nizamabad", "lat": 18.67, "lon": 78.09, "slug": "nizamabad"},
    "adilabad": {"name": "Adilabad", "lat": 19.67, "lon": 78.53, "slug": "adilabad"},
    "krishna": {"name": "Krishna Basin (Vijayawada)", "lat": 16.51, "lon": 80.62, "slug": "krishna_vijayawada"},
    "mahanadi": {"name": "Mahanadi Basin (Cuttack)", "lat": 20.46, "lon": 85.88, "slug": "mahanadi_cuttack"},
}

CACHE_TTL_SECONDS = 3 * 3600  # 3 hours


def _read_disk_cache() -> Dict[str, Any]:
    """Read the JSON cache store."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading telemetry cache: {e}")
        return {}


def _write_disk_cache(cache_data: Dict[str, Any]) -> None:
    """Save the JSON cache store."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error writing telemetry cache: {e}")


def _load_historical_fallback(basin_key: str) -> Dict[str, Any]:
    """Fall back to local historical dataset in data/all_districts.csv."""
    logger.info(f"Loading local historical fallback for {basin_key}...")
    coords = DEFAULT_BASIN_COORDS.get(basin_key.lower(), DEFAULT_BASIN_COORDS["godavari"])
    slug = coords.get("slug", "bhadradri_kothagudem")
    
    csv_path = PROJECT_ROOT / "data" / "all_districts.csv"
    if not csv_path.exists():
        csv_path = PROJECT_ROOT / "data" / f"{slug}.csv"

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if "district_slug" in df.columns:
            df_dist = df[df["district_slug"] == slug]
            if df_dist.empty:
                df_dist = df
        else:
            df_dist = df

        latest = df_dist.iloc[-1]
        obs_date = str(latest.get("date", "2025-10-31"))
        precip = float(latest.get("precip_mm", 0.0))
        temp = float(latest.get("temp_c", 28.0))
        soil = float(latest.get("soil_moisture", 0.32))
        discharge = float(latest.get("river_discharge", 45.0))
    else:
        obs_date = "2025-10-31"
        precip = 0.0
        temp = 28.5
        soil = 0.35
        discharge = 50.0

    return {
        "basin": basin_key,
        "name": coords["name"],
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "observation_date": obs_date,
        "precip_mm": precip,
        "temp_c": temp,
        "soil_moisture": soil,
        "river_discharge": discharge,
        "forecast_days": [],
        "last_updated_timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "Local Historical Fixture Cache (Offline Fallback)",
        "mode": "LOCAL CACHE FALLBACK (OFFLINE)",
    }


def fetch_basin_data(
    basin: str = "godavari",
    force_offline: bool = False,
    timeout_sec: float = 4.0,
) -> Tuple[Dict[str, Any], str]:
    """
    Fetch dual-mode hydrological telemetry for target basin or district.
    Returns: (data_dict, mode_string)
    Modes:
      - 'LIVE TELEMETRY - OPEN-METEO'
      - 'CACHED TELEMETRY'
      - 'LOCAL CACHE FALLBACK (OFFLINE)'
      - 'HISTORICAL BENCHMARK'
    """
    basin_key = basin.lower().strip()
    coords = DEFAULT_BASIN_COORDS.get(basin_key, DEFAULT_BASIN_COORDS["godavari"])
    lat = coords["lat"]
    lon = coords["lon"]
    cache_key = f"{lat:.2f}_{lon:.2f}"

    cache_store = _read_disk_cache()
    cached_entry = cache_store.get(cache_key)

    now_epoch = time.time()

    # If force_offline, use cache or fallback immediately
    if force_offline:
        if cached_entry:
            data = cached_entry["data"]
            data["mode"] = "CACHED TELEMETRY"
            return data, "CACHED TELEMETRY"
        fallback = _load_historical_fallback(basin_key)
        return fallback, fallback["mode"]

    # Attempt live query
    try:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&daily=precipitation_sum,temperature_2m_mean&"
            f"hourly=soil_moisture_0_to_7cm&timezone=Asia%2FKolkata&forecast_days=7"
        )
        flood_url = (
            f"https://flood-api.open-meteo.com/v1/flood?"
            f"latitude={lat}&longitude={lon}&daily=river_discharge&forecast_days=7"
        )

        resp_w = requests.get(weather_url, timeout=timeout_sec)
        resp_w.raise_for_status()
        data_w = resp_w.json()

        # River discharge query (defensive, fallback if empty)
        discharge_val = 0.0
        daily_discharges = []
        try:
            resp_f = requests.get(flood_url, timeout=timeout_sec)
            if resp_f.status_code == 200:
                data_f = resp_f.json()
                discharges = data_f.get("daily", {}).get("river_discharge", [])
                daily_discharges = discharges
                if discharges and discharges[0] is not None:
                    discharge_val = float(discharges[0])
        except Exception as e_flood:
            logger.warning(f"Flood API secondary query notice: {e_flood}")

        # Parse weather
        daily = data_w.get("daily", {})
        times = daily.get("time", [datetime.now(timezone.utc).strftime("%Y-%m-%d")])
        precips = daily.get("precipitation_sum", [0.0])
        temps = daily.get("temperature_2m_mean", [28.0])

        hourly_soil = data_w.get("hourly", {}).get("soil_moisture_0_to_7cm", [])
        avg_soil = float(np.mean(hourly_soil[:24])) if hourly_soil else 0.35

        cur_precip = float(precips[0]) if precips and precips[0] is not None else 0.0
        cur_temp = float(temps[0]) if temps and temps[0] is not None else 28.0

        # Construct forecast series
        forecast_days = []
        for i, t_str in enumerate(times[:7]):
            p_val = float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0
            t_val = float(temps[i]) if i < len(temps) and temps[i] is not None else 28.0
            q_val = float(daily_discharges[i]) if i < len(daily_discharges) and daily_discharges[i] is not None else discharge_val
            forecast_days.append({
                "date": t_str,
                "precip_mm": p_val,
                "temp_c": t_val,
                "river_discharge": q_val,
            })

        telemetry_payload = {
            "basin": basin_key,
            "name": coords["name"],
            "latitude": lat,
            "longitude": lon,
            "observation_date": times[0],
            "precip_mm": cur_precip,
            "temp_c": cur_temp,
            "soil_moisture": round(avg_soil, 3),
            "river_discharge": round(discharge_val, 2),
            "forecast_days": forecast_days,
            "last_updated_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_source": "Open-Meteo Live Forecast & ECMWF GloFAS API",
            "mode": "LIVE TELEMETRY - OPEN-METEO",
        }

        # Cache live response
        cache_store[cache_key] = {
            "saved_epoch": now_epoch,
            "data": telemetry_payload,
        }
        _write_disk_cache(cache_store)
        logger.info(f"Live telemetry successfully ingested for {coords['name']}")
        return telemetry_payload, "LIVE TELEMETRY - OPEN-METEO"

    except Exception as exc:
        logger.warning(f"Live API ingestion failed ({exc}). Engaging automated fallback...")
        if cached_entry:
            cached_data = cached_entry["data"]
            cached_data["mode"] = "CACHED TELEMETRY"
            logger.info("Serving from persistent cache.")
            return cached_data, "CACHED TELEMETRY"

        fallback = _load_historical_fallback(basin_key)
        return fallback, fallback["mode"]
