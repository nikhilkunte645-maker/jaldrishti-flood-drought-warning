"""
JalDrishti - Phase 8: Automated System Self-Test
Validates artifact existence, model integrity, coverage of predictions,
multilingual alert formatting, and drought status queries on random dates.
"""

import json
import logging
import random
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.alerts import get_alert, ALERTS
from src.drought import get_drought_status
from src.features import FEATURE_NAMES

# Ensure UTF-8 output encoding for console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JalDrishti.SelfTest")

DATA_DIR = Path("data")
MODELS_DIR = Path("models")


def run_selftest() -> bool:
    """Run comprehensive automated self-tests."""
    all_passed = True
    test_results = []

    def record_test(name: str, passed: bool, detail: str = ""):
        nonlocal all_passed
        if not passed:
            all_passed = False
        test_results.append({"Test": name, "Status": "PASS" if passed else "FAIL", "Detail": detail})
        status_str = "[PASS]" if passed else "[FAIL]"
        logger.info(f"{status_str} {name}: {detail}")

    # 1. Check critical files existence
    expected_files = [
        DATA_DIR / "all_districts.csv",
        DATA_DIR / "predictions.csv",
        DATA_DIR / "drought.csv",
        DATA_DIR / "shap_values.csv",
        DATA_DIR / "bhadradri_kothagudem.csv",
        DATA_DIR / "mulugu.csv",
        DATA_DIR / "nizamabad.csv",
        DATA_DIR / "adilabad.csv",
        MODELS_DIR / "flood_24h.joblib",
        MODELS_DIR / "flood_48h.joblib",
        MODELS_DIR / "flood_72h.joblib",
        MODELS_DIR / "thresholds.json",
        MODELS_DIR / "features.json",
        MODELS_DIR / "metrics.csv",
        MODELS_DIR / "backtest.json",
        MODELS_DIR / "backtest.html",
    ]

    missing = [str(f) for f in expected_files if not f.exists()]
    record_test("Files Existence", len(missing) == 0, f"Found {len(expected_files) - len(missing)}/{len(expected_files)} files. Missing: {missing}")

    # 2. Check models loading and dummy inference
    dummy_input = pd.DataFrame(np.ones((1, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    models_ok = True
    for h in ["24h", "48h", "72h"]:
        m_path = MODELS_DIR / f"flood_{h}.joblib"
        try:
            clf = joblib.load(m_path)
            prob = clf.predict_proba(dummy_input)[:, 1][0]
            if not (0.0 <= prob <= 1.0):
                models_ok = False
        except Exception as e:
            models_ok = False
            logger.error(f"Failed to load/predict with model {h}: {e}")
    record_test("Model Loading & Inference", models_ok, "All 3 XGBoost models loaded and verified inference")

    # 3. Check predictions coverage
    preds_df = pd.read_csv(DATA_DIR / "predictions.csv")
    districts_covered = set(preds_df["district_slug"].unique())
    expected_districts = {"bhadradri_kothagudem", "mulugu", "nizamabad", "adilabad"}
    has_all_districts = expected_districts.issubset(districts_covered)
    no_nan_probs = preds_df[["prob_24h", "prob_48h", "prob_72h"]].isna().sum().sum() == 0
    preds_ok = has_all_districts and no_nan_probs and len(preds_df) >= 5000
    record_test("Predictions Coverage", preds_ok, f"{len(preds_df)} rows, 4 districts covered, 0 NaN probabilities")

    # 4. Check all alert combinations format with no leftover braces
    alerts_ok = True
    braces_found = []
    for hazard in ["flood", "drought"]:
        for lvl in ["Low", "Medium", "High"]:
            for lang in ["en", "te", "hi"]:
                for dist in ["Bhadradri Kothagudem", "Mulugu", "Nizamabad", "Adilabad"]:
                    alert = get_alert(hazard, lvl, lang, dist, hours=72)
                    if "{" in alert or "}" in alert:
                        alerts_ok = False
                        braces_found.append(f"{hazard}-{lvl}-{lang}")
    record_test("Alerts Formatting", alerts_ok, f"Verified 72 templates across EN/TE/HI. Leftover braces: {braces_found}")

    # 5. Check drought queries on 20 random dates
    random.seed(42)
    sample_dates = random.sample(preds_df["date"].tolist(), 20)
    drought_ok = True
    for d in sample_dates:
        for dist_slug in expected_districts:
            try:
                res = get_drought_status(dist_slug, d)
                if res.get("drought_class") not in ("Normal", "Moderate", "Severe"):
                    drought_ok = False
            except Exception as e:
                drought_ok = False
                logger.error(f"Drought status query failed for {dist_slug} on {d}: {e}")
    record_test("Drought Queries (20 Random Dates)", drought_ok, f"Queried 20 random dates across 4 districts (80 lookups)")

    print("\n" + "=" * 80)
    print("                     JALDRISHTI SYSTEM SELF-TEST SUMMARY                       ")
    print("=" * 80)
    res_df = pd.DataFrame(test_results)
    print(res_df.to_string(index=False))
    print("=" * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = run_selftest()
    sys.exit(0 if success else 1)

