"""
JalDrishti - Explainable AI (TreeSHAP) Engine
Provides granular, plain-language hydrological feature attribution in English, Telugu, and Hindi.
Extracts top 3 risk-elevating (positive) and top 3 risk-suppressing (negative) drivers
from local TreeSHAP values for flood forecasting.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

# ==============================================================================
# TRILINGUAL HYDROLOGICAL FEATURE DICTIONARY
# ==============================================================================

FEATURE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "precip_roll_7d": {
        "en": "7-Day Cumulative Rainfall",
        "te": "గత 7 రోజుల వర్షపాతం",
        "hi": "पिछले 7 दिनों की कुल वर्षा",
    },
    "precip_roll_14d": {
        "en": "14-Day Cumulative Rainfall",
        "te": "గత 14 రోజుల వర్షపాతం",
        "hi": "पिछले 14 दिनों की कुल वर्षा",
    },
    "precip_roll_3d": {
        "en": "72h Cumulative Precipitation",
        "te": "గత 72 గంటల భారీ వర్షపాతం",
        "hi": "पिछले 72 घंटे की भारी वर्षा",
    },
    "precip_roll_1d": {
        "en": "Recent 24h Precipitation",
        "te": "గత 24 గంటల వర్షపాతం",
        "hi": "पिछले 24 घंटे की वर्षा",
    },
    "river_discharge": {
        "en": "Current River Discharge Rate",
        "te": "ప్రస్తుత నదీ ప్రవాహం",
        "hi": "वर्तमान नदी प्रवाह दर",
    },
    "river_discharge_lag_1d": {
        "en": "Previous Day River Flow",
        "te": "నిన్నటి నదీ ప్రవాహం",
        "hi": "पिछले दिन का नदी प्रवाह",
    },
    "river_discharge_lag_2d": {
        "en": "2-Day Prior River Flow",
        "te": "రెండు రోజుల క్రితం నదీ ప్రవాహం",
        "hi": "दो दिन पूर्व का नदी प्रवाह",
    },
    "river_discharge_lag_3d": {
        "en": "3-Day Prior River Flow",
        "te": "మూడు రోజుల క్రితం నదీ ప్రవాహం",
        "hi": "तीन दिन पूर्व का नदी प्रवाह",
    },
    "river_discharge_diff_1d": {
        "en": "1-Day River Surge Velocity",
        "te": "నదీ ప్రవాహ పెరుగుదల వేగం",
        "hi": "नदी प्रवाह वृद्धि वेग",
    },
    "soil_moisture": {
        "en": "Upper Soil Moisture Saturation",
        "te": "పై నేల తేమ సంతృప్తత",
        "hi": "ऊपरी मृदा नमी संतृप्ति",
    },
    "soil_moisture_diff_3d": {
        "en": "3-Day Soil Wetting Rate",
        "te": "3 రోజుల నేల తేమ పెరుగుదల",
        "hi": "3-दिवसीय मृदा नमी वृद्धि",
    },
    "month": {
        "en": "Monsoon Seasonal Timing",
        "te": "వర్షాకాల సీజన్ ప్రభావం",
        "hi": "मानसून मौसमी प्रभाव",
    },
}

# Fallbacks for raw column prefixes
PREFIX_CLEAN = {
    "shap_": "",
}


def clean_feature_name(raw_name: str) -> str:
    """Strip 'shap_' prefix and normalise string."""
    clean = raw_name
    for p, r in PREFIX_CLEAN.items():
        if clean.startswith(p):
            clean = clean[len(p):]
    return clean.strip()


def get_feature_label(raw_name: str, lang: str = "en") -> str:
    """Return localized label for a hydrological feature."""
    clean = clean_feature_name(raw_name)
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"
    if clean in FEATURE_TRANSLATIONS:
        return FEATURE_TRANSLATIONS[clean].get(lang_key, FEATURE_TRANSLATIONS[clean]["en"])
    return clean.replace("_", " ").title()


def format_driver_phrase(raw_name: str, shap_val: float, lang: str = "en") -> str:
    """
    Format a localized phrase like:
    EN: '72h Cumulative Precipitation (+28% risk)'
    TE: 'గత 72 గంటల భారీ వర్షపాతం (+28% ముప్పు)'
    HI: 'पिछले 72 घंटे की भारी वर्षा (+28% जोखिम)'
    """
    label = get_feature_label(raw_name, lang=lang)
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"

    # Convert SHAP log-odds shift approximately to indicative percentage contribution
    # Positive: increases log-odds; negative: decreases
    pct_est = int(round(abs(shap_val) * 15))
    sign = "+" if shap_val >= 0 else "-"

    if lang_key == "te":
        suffix = "ముప్పు" if shap_val >= 0 else "తగ్గింపు"
        return f"{label} ({sign}{pct_est}% {suffix})"
    elif lang_key == "hi":
        suffix = "जोखिम" if shap_val >= 0 else "राहत"
        return f"{label} ({sign}{pct_est}% {suffix})"
    else:
        suffix = "risk" if shap_val >= 0 else "reduction"
        return f"{label} ({sign}{pct_est}% {suffix})"


def extract_top_shap_drivers(
    shap_dict_or_row: Any,
    lang: str = "en",
    top_n: int = 3,
) -> Dict[str, Any]:
    """
    Given a series/dict of {feature_or_shap_feature: shap_value},
    extracts the top 3 risk-elevating (positive) and top 3 risk-suppressing (negative) drivers.
    Returns:
    {
        "positive": [{"feature": ..., "label": ..., "shap": float, "phrase": ...}, ...],
        "negative": [{"feature": ..., "label": ..., "shap": float, "phrase": ...}, ...],
        "summary": "Localized plain-language explanation string",
    }
    """
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"

    items = []
    if isinstance(shap_dict_or_row, pd.Series):
        series_dict = shap_dict_or_row.to_dict()
    elif isinstance(shap_dict_or_row, dict):
        series_dict = shap_dict_or_row
    else:
        series_dict = {}

    for k, v in series_dict.items():
        if k in ("date", "district", "district_slug"):
            continue
        try:
            val = float(v)
            if np.isnan(val):
                continue
            clean_k = clean_feature_name(k)
            label = get_feature_label(clean_k, lang=lang_key)
            phrase = format_driver_phrase(clean_k, val, lang=lang_key)
            items.append({
                "feature": clean_k,
                "label": label,
                "shap": val,
                "abs_shap": abs(val),
                "phrase": phrase,
            })
        except (ValueError, TypeError):
            continue

    pos = [x for x in items if x["shap"] > 0]
    neg = [x for x in items if x["shap"] < 0]

    pos.sort(key=lambda x: x["shap"], reverse=True)
    neg.sort(key=lambda x: x["shap"])  # most negative first

    top_pos = pos[:top_n]
    top_neg = neg[:top_n]

    # Build plain natural-language summary sentence
    summary = ""
    if top_pos:
        primary = top_pos[0]
        if lang_key == "te":
            summary = (
                f"ప్రధాన వరద కారణం: {primary['label']} ({primary['shap']:+.2f} TreeSHAP ప్రభావం). "
                f"ఇది రాబోయే 72 గంటల్లో వరద ముప్పును గణనీయంగా పెంచుతోంది."
            )
        elif lang_key == "hi":
            summary = (
                f"प्रमुख बाढ़ कारक: {primary['label']} ({primary['shap']:+.2f} TreeSHAP प्रभाव)। "
                f"यह आगामी 72 घंटों में बाढ़ जोखिम को तेजी से बढ़ा रहा है।"
            )
        else:
            summary = (
                f"Primary Flood Driver: {primary['label']} ({primary['shap']:+.2f} TreeSHAP impact), "
                f"substantially elevating 72h flood risk."
            )
    elif top_neg:
        primary = top_neg[0]
        if lang_key == "te":
            summary = (
                f"ప్రస్తుత పరిస్థితి నియంత్రణలో ఉంది: {primary['label']} ({primary['shap']:+.2f} TreeSHAP ప్రభావం) "
                f"వలన వరద సంభావ్యత తక్కువగా ఉంది."
            )
        elif lang_key == "hi":
            summary = (
                f"वर्तमान स्थिति नियंत्रण में है: {primary['label']} ({primary['shap']:+.2f} TreeSHAP प्रभाव) "
                f"के कारण बाढ़ की संभावना न्यून बनी हुई है।"
            )
        else:
            summary = (
                f"Conditions Stable: {primary['label']} ({primary['shap']:+.2f} TreeSHAP impact) "
                f"is actively suppressing flood probability."
            )
    else:
        if lang_key == "te":
            summary = "హైడ్రలాజికల్ సూచికలు సాధారణ పరిధిలో ఉన్నాయి."
        elif lang_key == "hi":
            summary = "हाइड्रोलॉजिकल संकेतक सामान्य सीमा में हैं।"
        else:
            summary = "Hydrological parameters remain within normal operating ranges."

    return {
        "positive": top_pos,
        "negative": top_neg,
        "summary": summary,
    }
