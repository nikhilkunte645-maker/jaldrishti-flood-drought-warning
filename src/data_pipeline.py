"""
JalDrishti - Phase 1: Data Pipeline
Fetches historical meteorological and hydrological data for 4 Godavari basin districts
from Open-Meteo Archive API and Open-Meteo Flood API.
Timeframe: 2015-01-01 to 2025-10-31.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("JalDrishti.DataPipeline")

# Target districts in Telangana Godavari Basin
DISTRICTS = [
    {
        "name": "Bhadradri Kothagudem",
        "slug": "bhadradri_kothagudem",
        "lat": 17.55,
        "lon": 80.62,
    },
    {
        "name": "Mulugu",
        "slug": "mulugu",
        "lat": 18.19,
        "lon": 80.00,
    },
    {
        "name": "Nizamabad",
        "slug": "nizamabad",
        "lat": 18.67,
        "lon": 78.09,
    },
    {
        "name": "Adilabad",
        "slug": "adilabad",
        "lat": 19.67,
        "lon": 78.53,
    },
]

START_DATE = "2015-01-01"
END_DATE = "2025-10-31"
TIMEZONE = "Asia/Kolkata"
REQUEST_SLEEP = 2.0  # seconds between API requests
MAX_RETRIES = 5

ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"
FLOOD_API_URL = "https://flood-api.open-meteo.com/v1/flood"


def fetch_with_retry(url: str, params: dict, max_retries: int = MAX_RETRIES) -> dict:
    """Make GET request with exponential backoff on errors and rate limits."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait_time = int(resp.headers.get("Retry-After", 2 ** attempt + 2))
                logger.warning(f"Rate limited (429). Backing off for {wait_time}s (Attempt {attempt}/{max_retries})...")
                time.sleep(wait_time)
            elif resp.status_code >= 500:
                wait_time = 2 ** attempt
                logger.warning(f"Server error ({resp.status_code}). Retrying in {wait_time}s (Attempt {attempt}/{max_retries})...")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error {resp.status_code}: {resp.text}")
                resp.raise_for_status()
        except (requests.RequestException, ConnectionError, TimeoutError) as e:
            if attempt == max_retries:
                logger.error(f"Final retry failed for {url}: {e}")
                raise
            wait_time = 2 ** attempt + 1
            logger.warning(f"Request exception {e}. Retrying in {wait_time}s (Attempt {attempt}/{max_retries})...")
            time.sleep(wait_time)
    raise RuntimeError(f"Failed to fetch data from {url} after {max_retries} attempts")


def fetch_yearly_chunk(lat: float, lon: float, start_chunk: str, end_chunk: str) -> pd.DataFrame:
    """Fetch weather (archive) and flood discharge for a single year chunk."""
    # 1. Fetch Archive API: precipitation, temp, soil moisture
    archive_params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_chunk,
        "end_date": end_chunk,
        "daily": ["precipitation_sum", "temperature_2m_mean"],
        "hourly": ["soil_moisture_0_to_7cm"],
        "timezone": TIMEZONE,
    }
    archive_data = fetch_with_retry(ARCHIVE_API_URL, archive_params)
    time.sleep(REQUEST_SLEEP)

    daily_dict = archive_data.get("daily", {})
    df_daily = pd.DataFrame({
        "date": daily_dict.get("time", []),
        "precip_mm": daily_dict.get("precipitation_sum", []),
        "temp_c": daily_dict.get("temperature_2m_mean", [])
    })

    hourly_dict = archive_data.get("hourly", {})
    df_hourly = pd.DataFrame({
        "time": hourly_dict.get("time", []),
        "soil_moisture": hourly_dict.get("soil_moisture_0_to_7cm", [])
    })
    if not df_hourly.empty:
        df_hourly["date"] = df_hourly["time"].str[:10]
        daily_sm = df_hourly.groupby("date")["soil_moisture"].mean().reset_index()
    else:
        daily_sm = pd.DataFrame(columns=["date", "soil_moisture"])

    # 2. Fetch Flood API: river discharge
    flood_params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_chunk,
        "end_date": end_chunk,
        "daily": ["river_discharge"],
    }
    flood_data = fetch_with_retry(FLOOD_API_URL, flood_params)
    time.sleep(REQUEST_SLEEP)

    flood_dict = flood_data.get("daily", {})
    df_flood = pd.DataFrame({
        "date": flood_dict.get("time", []),
        "river_discharge": flood_dict.get("river_discharge", [])
    })

    # Merge daily datasets
    merged = pd.merge(df_daily, daily_sm, on="date", how="left")
    merged = pd.merge(merged, df_flood, on="date", how="left")
    return merged


def fetch_district_data(district: dict, base_dir: Path) -> pd.DataFrame:
    """Fetch complete time series 2015-2025 for a district in yearly chunks."""
    slug = district["slug"]
    lat = district["lat"]
    lon = district["lon"]
    out_file = base_dir / f"{slug}.csv"
    cache_dir = base_dir / "cache" / slug
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Check if target file already exists and is complete
    if out_file.exists():
        try:
            existing = pd.read_csv(out_file)
            if len(existing) >= 3900 and existing["river_discharge"].isna().sum() == 0:
                logger.info(f"Target file {out_file} already exists and valid ({len(existing)} rows). Skipping fetch.")
                return existing
        except Exception as e:
            logger.warning(f"Could not read existing file {out_file}, re-fetching: {e}")

    logger.info(f"Fetching data for district '{district['name']}' ({slug}) at ({lat}, {lon})...")
    yearly_dfs = []

    years = list(range(2015, 2026))
    for year in years:
        chunk_start = f"{year}-01-01"
        chunk_end = f"{year}-12-31" if year < 2025 else END_DATE
        cache_file = cache_dir / f"{year}.csv"

        if cache_file.exists():
            logger.info(f"  Loading cached chunk for {year} from {cache_file.name}")
            df_year = pd.read_csv(cache_file)
        else:
            logger.info(f"  Fetching chunk {chunk_start} to {chunk_end}...")
            df_year = fetch_yearly_chunk(lat, lon, chunk_start, chunk_end)
            df_year.to_csv(cache_file, index=False)
            logger.info(f"  Saved cache for {year} ({len(df_year)} records)")

        yearly_dfs.append(df_year)

    combined = pd.concat(yearly_dfs, ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)

    # Ensure full date range
    expected_dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D").strftime("%Y-%m-%d")
    expected_df = pd.DataFrame({"date": expected_dates})
    combined = pd.merge(expected_df, combined, on="date", how="left")

    # Interpolate gaps up to 5 days
    cols_to_interpolate = ["precip_mm", "temp_c", "soil_moisture", "river_discharge"]
    missing_before = combined[cols_to_interpolate].isna().sum().to_dict()

    for col in cols_to_interpolate:
        # Linear interpolation with limit=5
        combined[col] = combined[col].interpolate(method="linear", limit=5)
        # Any edge NaNs filled with bfill/ffill
        combined[col] = combined[col].bfill().ffill()

    # Assert no NaNs remain
    nan_count = combined[cols_to_interpolate].isna().sum().sum()
    assert nan_count == 0, f"Error: {nan_count} NaNs remain in {slug} data after interpolation!"

    # Save finalized CSV
    combined = combined[["date", "precip_mm", "temp_c", "soil_moisture", "river_discharge"]]
    combined.to_csv(out_file, index=False)
    logger.info(f"Successfully saved {out_file} with {len(combined)} rows. Missing interpolated: {missing_before}")

    return combined


def audit_data_quality(df_all: pd.DataFrame) -> pd.DataFrame:
    """Generate data quality summary table and flag suspicious data."""
    records = []
    for district, grp in df_all.groupby("district"):
        n_rows = len(grp)
        min_date = grp["date"].min()
        max_date = grp["date"].max()

        flags = []
        if (grp["precip_mm"] < 0).any():
            flags.append("Negative precipitation")
        if (grp["river_discharge"] < 0).any():
            flags.append("Negative river discharge")
        if (grp["temp_c"] > 52).any():
            flags.append("Extreme heat (>52C)")
        if (grp["temp_c"] < 0).any():
            flags.append("Freezing temp (<0C)")
        if (grp["soil_moisture"] < 0).any() or (grp["soil_moisture"] > 1.0).any():
            flags.append("Soil moisture out of bounds [0, 1]")

        flag_str = ", ".join(flags) if flags else "CLEAN (No anomalies)"

        records.append({
            "District": district,
            "Rows": n_rows,
            "Date Range": f"{min_date} to {max_date}",
            "Precip Mean (mm)": round(float(grp["precip_mm"].mean()), 2),
            "Precip Max (mm)": round(float(grp["precip_mm"].max()), 2),
            "Temp Mean (°C)": round(float(grp["temp_c"].mean()), 2),
            "Discharge Mean (m³/s)": round(float(grp["river_discharge"].mean()), 2),
            "Discharge Max (m³/s)": round(float(grp["river_discharge"].max()), 2),
            "Soil Moisture Mean": round(float(grp["soil_moisture"].mean()), 3),
            "Quality Status": flag_str,
        })

    summary_df = pd.DataFrame(records)
    return summary_df


def run_pipeline():
    """Main execution entry point for Phase 1 data pipeline."""
    base_dir = Path("data")
    base_dir.mkdir(parents=True, exist_ok=True)

    all_district_dfs = []
    for dist in DISTRICTS:
        df_dist = fetch_district_data(dist, base_dir)
        df_dist_tagged = df_dist.copy()
        df_dist_tagged["district"] = dist["name"]
        df_dist_tagged["district_slug"] = dist["slug"]
        all_district_dfs.append(df_dist_tagged)

    # Save combined dataset
    df_all = pd.concat(all_district_dfs, ignore_index=True)
    all_districts_path = base_dir / "all_districts.csv"
    df_all.to_csv(all_districts_path, index=False)
    logger.info(f"Combined data saved to {all_districts_path} with {len(df_all)} total rows.")

    # Audit & report
    summary_df = audit_data_quality(df_all)
    print("\n" + "=" * 90)
    print("           JALDRISHTI PHASE 1 - DATA QUALITY & INTEGRITY REPORT           ")
    print("=" * 90)
    print(summary_df.to_string(index=False))
    print("=" * 90 + "\n")

    return df_all, summary_df


if __name__ == "__main__":
    run_pipeline()

