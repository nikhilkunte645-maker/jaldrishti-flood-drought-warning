"""
JalDrishti - Phase 7: Explainable AI (SHAP Engine)
Computes TreeSHAP explanations for the 72h flood forecasting model
and serializes local feature contributions for all test dates to data/shap_values.csv.
"""

import json
import logging
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import shap

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features import FEATURE_NAMES, prepare_modeling_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JalDrishti.SHAP")

DATA_DIR = Path("data")
MODELS_DIR = Path("models")

PLAIN_FEATURE_LABELS = {
    "precip_roll_7d": "7-Day Cumulative Rainfall",
    "precip_roll_14d": "14-Day Cumulative Rainfall",
    "precip_roll_3d": "3-Day Rainfall Accumulation",
    "precip_roll_1d": "Recent 24h Precipitation",
    "river_discharge": "Current River Discharge",
    "river_discharge_lag_1d": "Previous Day River Flow",
    "river_discharge_lag_2d": "2-Day Prior River Flow",
    "river_discharge_lag_3d": "3-Day Prior River Flow",
    "river_discharge_diff_1d": "1-Day River Flow Change",
    "soil_moisture": "Soil Moisture Saturation",
    "soil_moisture_diff_3d": "3-Day Soil Wetting Rate",
    "month": "Monsoon Seasonal Timing",
}


def compute_and_save_shap_values():
    """Compute local SHAP values for 72h model on all test records."""
    model_path = MODELS_DIR / "flood_72h.joblib"
    preds_path = DATA_DIR / "predictions.csv"
    thresholds_path = MODELS_DIR / "thresholds.json"
    all_districts_path = DATA_DIR / "all_districts.csv"

    if not model_path.exists() or not preds_path.exists():
        raise FileNotFoundError("Missing flood_72h.joblib or predictions.csv. Run Phase 2 first.")

    logger.info(f"Loading 72h model from {model_path}...")
    clf = joblib.load(model_path)

    logger.info("Loading dataset and reconstructing feature matrix...")
    df_all = pd.read_csv(all_districts_path)
    with open(thresholds_path, "r", encoding="utf-8") as f:
        thresholds = json.load(f)

    df_modeled = prepare_modeling_dataset(df_all, thresholds)
    df_test = df_modeled[df_modeled["date"] >= "2022-01-01"].copy().reset_index(drop=True)

    X_test = df_test[FEATURE_NAMES]

    logger.info(f"Computing TreeSHAP values for {len(X_test)} samples across {len(FEATURE_NAMES)} features...")
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_test)

    # In binary classification XGBoost, shap_values is a 2D array (n_samples, n_features)
    if isinstance(shap_values, list):
        shap_mat = shap_values[1]  # positive class
    else:
        shap_mat = shap_values

    # Build DataFrame
    shap_df = pd.DataFrame(shap_mat, columns=[f"shap_{col}" for col in FEATURE_NAMES])
    shap_df["district"] = df_test["district"]
    shap_df["district_slug"] = df_test["district_slug"]
    shap_df["date"] = df_test["date"]

    out_csv = DATA_DIR / "shap_values.csv"
    shap_df.to_csv(out_csv, index=False)
    logger.info(f"Successfully saved SHAP values to {out_csv} with {len(shap_df)} rows.")

    # Compute mean absolute SHAP for global ranking
    global_importance = pd.DataFrame({
        "feature": FEATURE_NAMES,
        "feature_label": [PLAIN_FEATURE_LABELS[f] for f in FEATURE_NAMES],
        "mean_abs_shap": np.abs(shap_mat).mean(axis=0),
    }).sort_values("mean_abs_shap", ascending=False)

    print("\n" + "=" * 80)
    print("                GLOBAL FEATURE ATTRIBUTION (72H MODEL - SHAP)                 ")
    print("=" * 80)
    print(global_importance.to_string(index=False))
    print("=" * 80 + "\n")

    return shap_df, global_importance


if __name__ == "__main__":
    compute_and_save_shap_values()

