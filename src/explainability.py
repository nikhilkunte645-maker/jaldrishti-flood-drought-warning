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


def get_farmer_explanation(shap_analysis: Dict[str, Any], lang: str = "en") -> str:
    """
    Generate an intuitive 'Explain Like a Farmer' 2-sentence breakdown
    mapping physical contributors to practical field realities in EN, TE, HI.
    """
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"
    pos = shap_analysis.get("positive", [])

    if not pos:
        if lang_key == "te":
            return (
                "నదీ ప్రవాహం ప్రస్తుతం సురక్షిత పరిమితుల్లో ఉంది, పొలాల్లో నేల తేమ కూడా అదుపులో ఉంది. "
                "రాబోయే 3 రోజుల్లో పంటలకు లేదా గ్రామాలకు ఎటువంటి ముంపు ముప్పు లేదు."
            )
        elif lang_key == "hi":
            return (
                "वर्तमान में नदी का जलस्तर सुरक्षित सीमा के भीतर है और खेतों की मिट्टी में अतिरिक्त जलभराव नहीं है। "
                "अगले 3 दिनों में फसलों या तटवर्ती गांवों में जलभराव का कोई खतरा नहीं है।"
            )
        else:
            return (
                "River flows remain safely within standard channel embankments and catchment soil is not oversaturated. "
                "No inundation threat to standing crops or low-lying pastures is anticipated over the next 72 hours."
            )

    p1 = pos[0]
    p1_feat = p1.get("feature", "")
    p1_label = p1.get("label", "Rainfall/Discharge")
    p1_pct = int(round(abs(p1.get("shap", 0.0)) * 15))

    p2_label = ""
    p2_pct = 0
    if len(pos) > 1:
        p2 = pos[1]
        p2_label = p2.get("label", "")
        p2_pct = int(round(abs(p2.get("shap", 0.0)) * 15))

    if lang_key == "te":
        if "discharge" in p1_feat or "river" in p1_feat:
            s1 = f"ఎగువ ప్రాంతాల నుంచి వస్తున్న నదీ ప్రవాహం ప్రస్తుత వరద ముప్పులో ప్రధానంగా {p1_pct}% ప్రభావం చూపుతోంది."
            if p2_label:
                s1 += f" దీనితో పాటు స్థానిక {p2_label} కూడా {p2_pct}% ముప్పును పెంచుతోంది."
            s2 = "మన గ్రామంలో వర్షం తాత్కాలికంగా ఆగిపోయినా, ఎగువ నుంచి భారీగా వచ్చే వరద నీటి వలన నది నీటిమట్టం ఇంకా పెరిగే ప్రమాదం ఉంది; కాబట్టి లోతట్టు పొలాలు మరియు పశువులను వెంటనే సురక్షిత ఎత్తైన ప్రాంతాలకు తరలించండి."
        elif "soil" in p1_feat:
            s1 = f"గత కొన్ని రోజులుగా కురిసిన వర్షాలకు నేల పూర్తిగా తడిసి ముద్దవడం వలన ({p1_pct}% ముప్పు ప్రభావం) కొత్తగా పడే వర్షపు నీరు భూమిలోకి ఇంకడం లేదు."
            s2 = "నేల నీటిని పీల్చుకోలేకపోవడం వలన స్వల్ప వర్షం పడినా వరద నీరు నేరుగా పంట పొలాల్లోకి ప్రవేశిస్తుంది; రైతులు కాలువల తూములను తెరిచి నీటిని బయటకు మళ్లించాలి."
        else:
            s1 = f"గత కొన్ని రోజులుగా స్థానికంగా కురుస్తున్న భారీ వర్షపాతం ప్రస్తుత వరద ముప్పుకు ప్రధానంగా {p1_pct}% కారణమవుతోంది."
            if p2_label:
                s1 += f" అలాగే {p2_label} కూడా తోడై ప్రవాహాన్ని వేగవంతం చేస్తోంది."
            s2 = "భారీ నీటి ఉధృతి వలన వాగులు, లోతట్టు వంతెనలు మునిగిపోయే అవకాశం ఉంది; కాబట్టి రైతులు పంట కాలువలు మరియు పంపుసెట్ల వద్ద జాగ్రత్తగా ఉండాలి."
        return f"{s1} {s2}"

    elif lang_key == "hi":
        if "discharge" in p1_feat or "river" in p1_feat:
            s1 = f"ऊपरी जलग्रहण क्षेत्र से आ रहा नदी का तेज बहाव वर्तमान चेतावनी में मुख्य रूप से {p1_pct}% योगदान दे रहा है।"
            if p2_label:
                s1 += f" इसके साथ स्थानीय {p2_label} भी {p2_pct}% जोखिम जोड़ रहा है।"
            s2 = "भले ही स्थानीय बारिश कुछ समय के लिए रुक जाए, ऊपरी बांधों से आ रहे भारी पानी के कारण नदी का जलस्तर लगातार बढ़ता रहेगा; अतः निचले खेतों से मवेशियों और पंप सेटों को तुरंत ऊंचे स्थानों पर पहुंचाएं।"
        elif "soil" in p1_feat:
            s1 = f"खेतों की मिट्टी अत्यधिक वर्षा से पूरी तरह संतृप्त हो चुकी है ({p1_pct}% जोखिम प्रभाव), जिससे अब नया वर्षाजल जमीन में नहीं समा रहा है।"
            s2 = "मिट्टी की जल-अवशोषण क्षमता समाप्त होने के कारण हल्की वर्षा भी तुरंत सतह पर तेज बहाव बनाएगी; किसान जल निकासी नालियों को तुरंत साफ रखें।"
        else:
            s1 = f"पिछले दिनों से लगातार हो रही भारी बारिश मौजूदा बाढ़ के खतरे का {p1_pct}% मुख्य कारण है।"
            if p2_label:
                s1 += f" साथ ही {p2_label} भी पानी के दबाव को बढ़ा रहा है।"
            s2 = "खेतों और निचले रास्तों पर तेजी से पानी भरने की संभावना है; इसलिए किसान भाई रपटों को पार न करें और कटी हुई फसलों को सुरक्षित शेड में रखें।"
        return f"{s1} {s2}"

    else:
        if "discharge" in p1_feat or "river" in p1_feat:
            s1 = f"Upstream river discharge and catchment inflow account for approximately {p1_pct}% of the current flood alert level."
            if p2_label:
                s1 += f" Simultaneously, localized {p2_label} contributes an additional {p2_pct}% to runoff pressure."
            s2 = "Even if local rainfall ceases temporarily, river levels will continue to rise rapidly due to upstream drainage; frontline farmers should immediately relocate livestock and pump machinery to designated high ground."
        elif "soil" in p1_feat:
            s1 = f"Continuous antecedent rainfall has saturated the topsoil mantle ({p1_pct}% risk impact), leaving the catchment with zero infiltration capacity."
            s2 = "Because the saturated ground cannot absorb further moisture, any subsequent showers will convert immediately into overland flood runoff across low-lying paddy acreage."
        else:
            s1 = f"Persistent cumulative rainfall across the upper watershed is the primary driver ({p1_pct}% risk contribution) elevating the 72h flood threat."
            if p2_label:
                s1 += f" Saturated river discharge from {p2_label} further accelerates crest velocity."
            s2 = "Low-level causeways and field channels face rapid inundation; agricultural workers are advised to avoid crossing riverine causeways and safeguard grain storage."
        return f"{s1} {s2}"

