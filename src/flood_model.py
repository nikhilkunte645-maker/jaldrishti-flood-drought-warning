"""
JalDrishti - Phase 2: Flood Modeling Engine
Trains XGBoost classifiers for 24h, 48h, and 72h forward flood horizons.
Evaluates against a naive persistence baseline and saves test predictions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from xgboost import XGBClassifier

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features import (
    FEATURE_NAMES,
    compute_district_thresholds,
    prepare_modeling_dataset,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JalDrishti.FloodModel")

MODELS_DIR = Path("models")
DATA_DIR = Path("data")
HORIZONS = ["24h", "48h", "72h"]


def train_and_evaluate_models():
    """Execute complete training, evaluation, and serialization workflow."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    all_districts_csv = DATA_DIR / "all_districts.csv"

    if not all_districts_csv.exists():
        raise FileNotFoundError(f"Missing {all_districts_csv}. Run src/data_pipeline.py first.")

    logger.info(f"Loading data from {all_districts_csv}...")
    df_all = pd.read_csv(all_districts_csv)

    # 1. Compute training thresholds (2015-2021)
    thresholds = compute_district_thresholds(df_all, train_end_date="2021-12-31")
    thresholds_path = MODELS_DIR / "thresholds.json"
    with open(thresholds_path, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)
    logger.info(f"Saved 95th percentile training thresholds to {thresholds_path}: {thresholds}")

    # 2. Engineer features and targets
    df_modeled = prepare_modeling_dataset(df_all, thresholds)

    # 3. Time-based split: Train (2015-2021), Test (2022-2025)
    train_mask = df_modeled["date"] <= "2021-12-31"
    test_mask = df_modeled["date"] >= "2022-01-01"

    df_train = df_modeled[train_mask].copy()
    df_test = df_modeled[test_mask].copy()

    logger.info(f"Dataset split: Train={len(df_train)} rows (2015-2021), Test={len(df_test)} rows (2022-2025)")

    # Save feature names
    features_path = MODELS_DIR / "features.json"
    with open(features_path, "w", encoding="utf-8") as f:
        json.dump(FEATURE_NAMES, f, indent=2)

    metrics_records = []
    test_preds_df = df_test.copy()

    for h in HORIZONS:
        target_col = f"target_{h}"
        valid_col = f"valid_{target_col}"

        # Filter valid targets
        train_h = df_train[df_train[valid_col]].copy()
        test_h = df_test[df_test[valid_col]].copy()

        X_train = train_h[FEATURE_NAMES]
        y_train = train_h[target_col].astype(int)
        X_test = test_h[FEATURE_NAMES]
        y_test = test_h[target_col].astype(int)

        n_pos = int(y_train.sum())
        n_neg = len(y_train) - n_pos
        scale_pos = (n_neg / max(n_pos, 1))

        logger.info(f"--- Training {h} Model (Train pos: {n_pos}/{len(y_train)}, scale_pos_weight: {scale_pos:.2f}) ---")

        clf = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric="logloss",
        )
        clf.fit(X_train, y_train)

        # Save model artifact
        model_path = MODELS_DIR / f"flood_{h}.joblib"
        joblib.dump(clf, model_path)
        logger.info(f"Saved model artifact to {model_path}")

        # Model predictions
        probs = clf.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)

        # Naive Baseline: "Tomorrow equals today" (persistence)
        # If river_discharge today is already flooding, predict flood for horizon
        naive_preds = test_h["flood_today"].astype(int).values

        # Compute Model Metrics
        cm = confusion_matrix(y_test, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        auc = roc_auc_score(y_test, probs) if len(np.unique(y_test)) > 1 else 0.5

        # Compute Naive Baseline Metrics
        b_cm = confusion_matrix(y_test, naive_preds, labels=[0, 1])
        b_tn, b_fp, b_fn, b_tp = b_cm.ravel() if b_cm.size == 4 else (0, 0, 0, 0)
        b_prec = precision_score(y_test, naive_preds, zero_division=0)
        b_rec = recall_score(y_test, naive_preds, zero_division=0)
        b_f1 = f1_score(y_test, naive_preds, zero_division=0)

        # Record metrics for both
        metrics_records.append({
            "Horizon": h,
            "Model": "XGBoost (JalDrishti)",
            "Precision": round(float(prec), 4),
            "Recall": round(float(rec), 4),
            "F1-Score": round(float(f1), 4),
            "ROC-AUC": round(float(auc), 4),
            "False Alarms (FP)": int(fp),
            "Missed Events (FN)": int(fn),
            "True Positives (TP)": int(tp),
            "True Negatives (TN)": int(tn),
        })

        metrics_records.append({
            "Horizon": h,
            "Model": "Naive Baseline (Persistence)",
            "Precision": round(float(b_prec), 4),
            "Recall": round(float(b_rec), 4),
            "F1-Score": round(float(b_f1), 4),
            "ROC-AUC": 0.5,
            "False Alarms (FP)": int(b_fp),
            "Missed Events (FN)": int(b_fn),
            "True Positives (TP)": int(b_tp),
            "True Negatives (TN)": int(b_tn),
        })

        # Add predictions to test_preds_df
        full_X_test = test_preds_df[FEATURE_NAMES]
        test_preds_df[f"prob_{h}"] = clf.predict_proba(full_X_test)[:, 1].round(4)
        test_preds_df[f"pred_{h}"] = (test_preds_df[f"prob_{h}"] >= 0.5).astype(int)

    # Save metrics table
    metrics_df = pd.DataFrame(metrics_records)
    metrics_path = MODELS_DIR / "metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)
    logger.info(f"Saved model metrics to {metrics_path}")

    # Save test predictions CSV
    output_cols = [
        "district",
        "district_slug",
        "date",
        "precip_mm",
        "temp_c",
        "soil_moisture",
        "river_discharge",
        "flood_threshold",
        "flood_today",
        "target_24h",
        "target_48h",
        "target_72h",
        "prob_24h",
        "prob_48h",
        "prob_72h",
        "pred_24h",
        "pred_48h",
        "pred_72h",
    ]
    predictions_path = DATA_DIR / "predictions.csv"
    test_preds_df[output_cols].to_csv(predictions_path, index=False)
    logger.info(f"Saved test predictions to {predictions_path} with {len(test_preds_df)} rows")

    print("\n" + "=" * 105)
    print("                     JALDRISHTI FLOOD MODEL EVALUATION VS BASELINE                    ")
    print("=" * 105)
    print(metrics_df.to_string(index=False))
    print("=" * 105 + "\n")

    return metrics_df, test_preds_df


if __name__ == "__main__":
    train_and_evaluate_models()
