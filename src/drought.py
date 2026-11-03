"""
JalDrishti - Phase 4: Drought Monitoring Engine
Calculates SPI-1, SPI-3 (Standardized Precipitation Index via Gamma fit with zero-rain handling)
and Soil Moisture Z-Score Anomalies against historical calendar-month baselines.
Classifies drought severity into Normal, Moderate, or Severe.
Saves data/drought.csv and exports get_drought_status(district, date).
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JalDrishti.Drought")

DATA_DIR = Path("data")


def fit_gamma_and_compute_spi(series: pd.Series, baseline_mask: pd.Series) -> pd.Series:
    """
    Fits Gamma distribution on baseline period with rigorous zero-rain handling
    and returns SPI for the entire series.
    Probability of zero: q = N_zeros / N
    H(x) = q + (1 - q) * G(x)
    SPI = norm.ppf(H(x))
    """
    baseline_vals = series[baseline_mask].dropna().values
    if len(baseline_vals) == 0:
        return pd.Series(0.0, index=series.index)

    n_total = len(baseline_vals)
    pos_mask = baseline_vals > 0.001
    n_pos = int(pos_mask.sum())
    q = (n_total - n_pos) / n_total

    # Edge case: zero rainfall in all baseline periods
    if n_pos < 3:
        # All dry: define 0 rain as median (0.0 SPI) and positive rain as positive SPI
        res = []
        for x in series:
            if pd.isna(x):
                res.append(np.nan)
            elif x <= 0.001:
                res.append(0.0)
            else:
                res.append(1.0)
        return pd.Series(res, index=series.index)

    pos_vals = baseline_vals[pos_mask]
    try:
        # Fit Gamma distribution with location fixed at 0
        alpha, loc, scale = stats.gamma.fit(pos_vals, floc=0)
    except Exception as e:
        logger.warning(f"Gamma fit failed ({e}), using empirical normal fallback")
        mean = float(np.mean(baseline_vals))
        std = float(np.std(baseline_vals)) or 1.0
        return ((series - mean) / std).clip(-3.5, 3.5)

    spi_vals = []
    eps = 1e-6
    for val in series:
        if pd.isna(val):
            spi_vals.append(np.nan)
            continue
        if val <= 0.001:
            # For 0 rain, cumulative probability is q (use midpoint q/2 for unbiased SPI)
            p = max(eps, q / 2.0)
        else:
            g_val = stats.gamma.cdf(val, alpha, loc=loc, scale=scale)
            p = q + (1.0 - q) * g_val
            p = np.clip(p, eps, 1.0 - eps)
        spi = float(stats.norm.ppf(p))
        spi_vals.append(float(np.clip(spi, -3.5, 3.5)))

    return pd.Series(spi_vals, index=series.index)


def compute_drought_indices():
    """Compute SPI-1, SPI-3, and Soil Moisture anomalies for all districts."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_districts_csv = DATA_DIR / "all_districts.csv"
    if not all_districts_csv.exists():
        raise FileNotFoundError(f"Missing {all_districts_csv}. Run data_pipeline.py first.")

    df_all = pd.read_csv(all_districts_csv)
    df_all["date_dt"] = pd.to_datetime(df_all["date"])
    df_all["year"] = df_all["date_dt"].dt.year
    df_all["month"] = df_all["date_dt"].dt.month
    df_all["year_month"] = df_all["date_dt"].dt.to_period("M")

    all_drought_records = []

    for dist_slug, dist_daily in df_all.groupby("district_slug"):
        dist_name = dist_daily["district"].iloc[0]
        logger.info(f"Computing drought metrics for {dist_name} ({dist_slug})...")

        # 1. Monthly aggregation for SPI
        monthly_df = (
            dist_daily.groupby(["year_month", "year", "month"])
            .agg(
                precip_monthly=("precip_mm", "sum"),
                soil_moisture_mean=("soil_moisture", "mean"),
            )
            .reset_index()
        )
        monthly_df["date_start"] = monthly_df["year_month"].dt.to_timestamp().dt.strftime("%Y-%m-%d")

        # Rolling 3-month precipitation sum for SPI-3
        monthly_df["precip_3m"] = monthly_df["precip_monthly"].rolling(window=3, min_periods=1).sum()

        baseline_monthly_mask = monthly_df["year"] <= 2021

        # Fit SPI per calendar month (1..12) to account for monsoon seasonality
        monthly_df["spi_1"] = np.nan
        monthly_df["spi_3"] = np.nan

        for m in range(1, 13):
            m_mask = monthly_df["month"] == m
            if not m_mask.any():
                continue
            m_baseline = baseline_monthly_mask & m_mask

            # SPI-1
            spi_1_m = fit_gamma_and_compute_spi(monthly_df.loc[m_mask, "precip_monthly"], m_baseline)
            monthly_df.loc[m_mask, "spi_1"] = spi_1_m

            # SPI-3
            spi_3_m = fit_gamma_and_compute_spi(monthly_df.loc[m_mask, "precip_3m"], m_baseline)
            monthly_df.loc[m_mask, "spi_3"] = spi_3_m

        # 2. Daily Soil Moisture Anomaly vs calendar month baseline (2015-2021)
        dist_daily_proc = dist_daily.copy().sort_values("date").reset_index(drop=True)
        baseline_daily_mask = dist_daily_proc["year"] <= 2021

        # Compute calendar-month baseline stats
        sm_baseline_stats = (
            dist_daily_proc[baseline_daily_mask]
            .groupby("month")["soil_moisture"]
            .agg(sm_month_mean="mean", sm_month_std="std")
            .reset_index()
        )
        # Handle zero std
        sm_baseline_stats["sm_month_std"] = sm_baseline_stats["sm_month_std"].replace(0, 0.05).fillna(0.05)

        dist_daily_proc = pd.merge(dist_daily_proc, sm_baseline_stats, on="month", how="left")
        dist_daily_proc["sm_anomaly_z"] = (
            (dist_daily_proc["soil_moisture"] - dist_daily_proc["sm_month_mean"])
            / dist_daily_proc["sm_month_std"]
        ).clip(-4.0, 4.0).round(3)

        # Merge monthly SPI back to daily dates
        dist_daily_proc["year_month"] = dist_daily_proc["date_dt"].dt.to_period("M")
        spi_lookup = monthly_df[["year_month", "precip_monthly", "spi_1", "spi_3"]].copy()
        dist_daily_proc = pd.merge(dist_daily_proc, spi_lookup, on="year_month", how="left")

        # Classify Drought:
        # Standard: Normal (> -1.0), Moderate (-1.5 to -1.0), Severe (< -1.5)
        # Multi-index composite: evaluates minimum of SPI-3 and Soil Moisture Anomaly
        def classify_drought(row):
            spi3 = row["spi_3"] if not pd.isna(row["spi_3"]) else 0.0
            sm_z = row["sm_anomaly_z"] if not pd.isna(row["sm_anomaly_z"]) else 0.0
            worst_index = min(spi3, sm_z)
            if worst_index < -1.5:
                return "Severe"
            elif worst_index < -1.0:
                return "Moderate"
            else:
                return "Normal"

        dist_daily_proc["drought_class"] = dist_daily_proc.apply(classify_drought, axis=1)

        cols_to_keep = [
            "district",
            "district_slug",
            "date",
            "precip_mm",
            "soil_moisture",
            "precip_monthly",
            "spi_1",
            "spi_3",
            "sm_month_mean",
            "sm_month_std",
            "sm_anomaly_z",
            "drought_class",
        ]
        all_drought_records.append(dist_daily_proc[cols_to_keep])

    combined_drought = pd.concat(all_drought_records, ignore_index=True)
    drought_csv_path = DATA_DIR / "drought.csv"
    combined_drought.to_csv(drought_csv_path, index=False)
    logger.info(f"Saved complete drought metrics to {drought_csv_path} with {len(combined_drought)} records.")

    # Summary breakdown
    summary = combined_drought.groupby(["district", "drought_class"]).size().unstack(fill_value=0)
    print("\n" + "=" * 80)
    print("                    JALDRISHTI DROUGHT CLASSIFICATION SUMMARY                  ")
    print("=" * 80)
    print(summary.to_string())
    print("=" * 80 + "\n")

    return combined_drought


# Global cache for get_drought_status
_DROUGHT_CACHE: Optional[pd.DataFrame] = None


def get_drought_status(district: str, date: str) -> Dict[str, Union[str, float]]:
    """
    Look up drought status for a district on a given date.
    Args:
        district: Name or slug of the district (e.g. 'Bhadradri Kothagudem' or 'bhadradri_kothagudem')
        date: YYYY-MM-DD string
    Returns:
        dict with keys: district, date, spi_1, spi_3, sm_anomaly_z, drought_class, soil_moisture
    """
    global _DROUGHT_CACHE
    drought_csv_path = DATA_DIR / "drought.csv"

    if _DROUGHT_CACHE is None:
        if not drought_csv_path.exists():
            compute_drought_indices()
        _DROUGHT_CACHE = pd.read_csv(drought_csv_path)

    df = _DROUGHT_CACHE
    district_clean = str(district).lower().replace(" ", "_")
    dist_df = df[
        (df["district_slug"] == district_clean)
        | (df["district"].str.lower() == str(district).lower())
    ]

    if dist_df.empty:
        return {
            "district": district,
            "date": date,
            "spi_1": 0.0,
            "spi_3": 0.0,
            "sm_anomaly_z": 0.0,
            "drought_class": "Normal",
            "error": "District not found",
        }

    # Match exact date
    match = dist_df[dist_df["date"] == str(date)]
    if not match.empty:
        row = match.iloc[0]
    else:
        # Preceding date fallback
        earlier = dist_df[dist_df["date"] <= str(date)]
        row = earlier.iloc[-1] if not earlier.empty else dist_df.iloc[0]

    return {
        "district": str(row["district"]),
        "district_slug": str(row["district_slug"]),
        "date": str(row["date"]),
        "spi_1": round(float(row["spi_1"]), 2) if not pd.isna(row["spi_1"]) else 0.0,
        "spi_3": round(float(row["spi_3"]), 2) if not pd.isna(row["spi_3"]) else 0.0,
        "soil_moisture": round(float(row["soil_moisture"]), 3) if not pd.isna(row["soil_moisture"]) else 0.0,
        "sm_anomaly_z": round(float(row["sm_anomaly_z"]), 2) if not pd.isna(row["sm_anomaly_z"]) else 0.0,
        "drought_class": str(row["drought_class"]),
    }


if __name__ == "__main__":
    compute_drought_indices()
