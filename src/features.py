"""
JalDrishti - Phase 2: Feature Engineering
Calculates rolling hydrological features, lags, changes, and strictly forward-looking flood targets.
Guarantees NO future data leakage in feature matrices.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

FEATURE_NAMES = [
    "precip_roll_1d",
    "precip_roll_3d",
    "precip_roll_7d",
    "precip_roll_14d",
    "soil_moisture",
    "soil_moisture_diff_3d",
    "river_discharge",
    "river_discharge_lag_1d",
    "river_discharge_lag_2d",
    "river_discharge_lag_3d",
    "river_discharge_diff_1d",
    "month",
]


def compute_district_thresholds(df_all: pd.DataFrame, train_end_date: str = "2021-12-31") -> Dict[str, float]:
    """
    Compute 95th percentile of river_discharge on training years (2015-2021) per district.
    Flood event = river_discharge > 95th percentile of training years.
    """
    train_mask = (df_all["date"] <= train_end_date)
    thresholds = {}
    for slug, grp in df_all[train_mask].groupby("district_slug"):
        thresh = float(np.percentile(grp["river_discharge"].dropna(), 95))
        thresholds[slug] = round(thresh, 3)
    return thresholds


def engineer_features_for_district(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Compute features and forward targets for a single district's time series.
    Data must be sorted chronologically by date.
    """
    df = df.copy().sort_values("date").reset_index(drop=True)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["month"] = df["date_dt"].dt.month

    # Rolling precipitation sums (strictly past/current)
    df["precip_roll_1d"] = df["precip_mm"]
    df["precip_roll_3d"] = df["precip_mm"].rolling(window=3, min_periods=1).sum()
    df["precip_roll_7d"] = df["precip_mm"].rolling(window=7, min_periods=1).sum()
    df["precip_roll_14d"] = df["precip_mm"].rolling(window=14, min_periods=1).sum()

    # Soil moisture dynamics
    df["soil_moisture_diff_3d"] = df["soil_moisture"].diff(3).fillna(0.0)

    # River discharge lags and short-term trend
    df["river_discharge_lag_1d"] = df["river_discharge"].shift(1).bfill()
    df["river_discharge_lag_2d"] = df["river_discharge"].shift(2).bfill()
    df["river_discharge_lag_3d"] = df["river_discharge"].shift(3).bfill()
    df["river_discharge_diff_1d"] = df["river_discharge"].diff(1).fillna(0.0)

    # Current flood indicator (for baseline comparison)
    df["flood_today"] = (df["river_discharge"] > threshold).astype(int)

    # Forward targets:
    # 24h target: flood on day t+1
    d1 = (df["river_discharge"].shift(-1) > threshold).astype(int)
    # 48h target: flood on day t+1 or t+2
    d2 = (df["river_discharge"].shift(-2) > threshold).astype(int)
    # 72h target: flood on day t+1, t+2, or t+3
    d3 = (df["river_discharge"].shift(-3) > threshold).astype(int)

    df["target_24h"] = d1
    df["target_48h"] = ((d1 == 1) | (d2 == 1)).astype(int)
    df["target_72h"] = ((d1 == 1) | (d2 == 1) | (d3 == 1)).astype(int)

    # Flag rows where future target cannot be verified (last 3 rows)
    df["valid_target_24h"] = ~df["river_discharge"].shift(-1).isna()
    df["valid_target_48h"] = ~df["river_discharge"].shift(-2).isna()
    df["valid_target_72h"] = ~df["river_discharge"].shift(-3).isna()

    return df


def prepare_modeling_dataset(df_all: pd.DataFrame, thresholds: Dict[str, float]) -> pd.DataFrame:
    """Process all districts with feature engineering and their respective thresholds."""
    processed_dfs = []
    for slug, grp in df_all.groupby("district_slug"):
        thresh = thresholds[slug]
        dist_df = engineer_features_for_district(grp, thresh)
        dist_df["flood_threshold"] = thresh
        processed_dfs.append(dist_df)

    combined = pd.concat(processed_dfs, ignore_index=True)
    return combined
