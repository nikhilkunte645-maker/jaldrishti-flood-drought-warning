"""
JalDrishti - Multilingual Warning & Disaster Dispatch Generator
Generates localized, clear, and actionable emergency alerts in English, Telugu, and Hindi.
Includes tiered civil protection stages and automated translation disclosure.
"""

from typing import Dict, List, Optional

# ==============================================================================
# OFFICIAL TRANSLATION DISCLAIMER
# ==============================================================================
DISCLAIMER_TAG = "[⚠️ Automated Draft Translation: Pending District Public Relations Officer (PRO) Native Review]"

# ==============================================================================
# MULTILINGUAL ALERT TEMPLATES
# Validated against state disaster management emergency phraseology (NDMA / TGSDMA).
# ==============================================================================

ALERTS: Dict[str, Dict[str, Dict[str, str]]] = {
    "flood": {
        "Low": {
            "en": "Normal conditions in {district}. No flood threat expected within next {hours} hours. Rivers flowing within safe banks.",
            "te": "{district} పరిధిలో గోదావరి నది ప్రవాహం సురక్షిత పరిమితుల్లో ఉంది. రాబోయే {hours} గంటల్లో వరద ముప్పు లేదు.",
            "hi": "{district} में गोदावरी नदी का जलस्तर सामान्य है। अगले {hours} घंटों में किसी भी बाढ़ का खतरा नहीं है।",
        },
        "Medium": {
            "en": "Flood Advisory: Rising water levels in {district}. Moderate flood risk within {hours} hours. Farmers and riverside residents should stay alert.",
            "te": "హెచ్చరిక: {district} లో నదీ ప్రవాహం పెరుగుతోంది. లోతట్టు గ్రామాల ప్రజలు మరియు రైతులు అప్రమత్తంగా ఉండాలి.",
            "hi": "चेतावनी: {district} में नदी का जलस्तर बढ़ रहा है। तटवर्ती क्षेत्रों के निवासी सतर्क रहें।",
        },
        "High": {
            "en": "CRITICAL FLOOD WARNING for {district}! High risk of inundation within next {hours} hours. Move to higher ground immediately and follow disaster response orders.",
            "te": "తీవ్ర హెచ్చరిక: రాబోయే {hours} గంటల్లో {district} పరిధిలో గోదావరి వరద ప్రవాహం ప్రమాద స్థాయికి చేరే అవకాశం ఉంది. లోతట్టు ప్రాంతాల ప్రజలు వెంటనే ఎత్తైన ప్రాంతాలకు తరలి వెళ్లండి.",
            "hi": "गंभीर चेतावनी: अगले {hours} घंटों के भीतर {district} में गोदावरी नदी का जलस्तर खतरे के निशान को पार करने की संभावना है। निचले इलाकों से तुरंत सुरक्षित स्थानों पर जाएं।",
        },
    },
    "drought": {
        "Low": {
            "en": "Moisture levels in {district} are normal. No immediate drought stress detected. Agricultural conditions stable.",
            "te": "{district} లో నేల తేమ మరియు వర్షపాతం సాధారణ స్థాయిలో ఉన్నాయి. ఎటువంటి కరవు ముప్పు లేదు.",
            "hi": "{district} में नमी और वर्षा का स्तर सामान्य है। सूखे का कोई तत्काल खतरा नहीं है।",
        },
        "Medium": {
            "en": "Drought Advisory: Moderate moisture deficit in {district}. Conserve irrigation water and monitor standing crops for moisture stress.",
            "te": "కరవు హెచ్చరిక: {district} లో మోస్తరు తేమ కొరత ఉంది. సాగునీటిని పొదుపుగా వాడండి మరియు పంటలను జాగ్రత్తగా గమనించండి.",
            "hi": "सूखा परामर्श: {district} में मध्यम नमी की कमी दर्ज की गई है। सिंचाई के पानी का सावधानी से उपयोग करें।",
        },
        "High": {
            "en": "SEVERE DROUGHT ALERT for {district}! Critical precipitation deficit and depleted soil moisture. Initiate emergency water conservation and crop protection measures.",
            "te": "తీవ్ర కరవు సూచన: {district} లో నేలలో తేమ శాతం ప్రమాదకరంగా తగ్గింది. తక్షణ నీటి సంరక్షణ విధానాలు పాటించండి.",
            "hi": "गंभीर सूखा परामर्श: {district} में मृदा नमी (Soil Moisture) अत्यंत न्यून स्तर पर है। तत्काल जल संरक्षण प्रबंधन लागू करें।",
        },
    },
}

# ==============================================================================
# TIERED CIVIL PROTECTION ACTION STAGES
# ==============================================================================

TIERED_CIVIL_ACTIONS: Dict[str, Dict[str, str]] = {
    "Stage 1": {
        "en": "Stage 1 (Advisory Alert): Monitor local catchment gauges, inspect drainage channels, and avoid low-level causeways.",
        "te": "దశ 1 (ముందస్తు హెచ్చరిక): స్థానిక నీటి గేట్లను గమనించండి, కాలువల పూడికతీత పరిశీలించండి, లోతట్టు వంతెనలను దాటవద్దు.",
        "hi": "चरण 1 (सलाहकारी चेतावनी): स्थानीय जल स्तर पर नजर रखें, जल निकासी की जांच करें और निचले रपटों को पार न करें।",
    },
    "Stage 2": {
        "en": "Stage 2 (Evacuate Livestock & Low-lying Farms): Move livestock, heavy pump sets, and harvested produce to designated higher ground immediately.",
        "te": "దశ 2 (పశువులు మరియు లోతట్టు పొలాల తరలింపు): పశువులు, మోటారు పంపు సెట్లు, ధాన్యపు బస్తాలను వెంటనే సురక్షిత ఎత్తైన ప్రాంతాలకు తరలించండి.",
        "hi": "चरण 2 (पशुधन और निचले खेतों की निकासी): मवेशियों, पंप मशीनों और कटी हुई फसलों को तुरंत सुरक्षित ऊंचे स्थानों पर ले जाएं।",
    },
    "Stage 3": {
        "en": "Stage 3 (Immediate High-Elevation Relocation): Mandatory evacuation for riverside wards to designated multi-purpose cyclone/flood shelters.",
        "te": "దశ 3 (వెంటనే సురక్షిత ప్రాంతాలకు తరలింపు): నదీ తీర ప్రాంతాల ప్రజలు వెంటనే ప్రభుత్వ పునరావాస కేంద్రాలు / వరద సహాయ శిబిరాలకు వెళ్ళాలి.",
        "hi": "चरण 3 (तत्काल उच्च-स्थान स्थानांतरण): नदी किनारे की बस्तियों के लिए आपदा राहत केंद्रों में अनिवार्य सुरक्षित निकासी।",
    },
}


def get_alert(
    hazard: str,
    level: str,
    lang: str,
    district: str,
    hours: Optional[int] = 72,
) -> str:
    """Retrieve formatted alert message."""
    hazard_key = hazard.lower()
    if hazard_key not in ALERTS:
        hazard_key = "flood"

    level_map = {
        "normal": "Low",
        "low": "Low",
        "moderate": "Medium",
        "medium": "Medium",
        "severe": "High",
        "high": "High",
    }
    level_key = level_map.get(str(level).lower(), "Low")
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"

    template = ALERTS[hazard_key][level_key].get(lang_key)
    if not template:
        template = ALERTS[hazard_key][level_key]["en"]

    h_val = hours if hours is not None else 72
    formatted = template.format(district=district, hours=h_val)
    return formatted


def get_tiered_civil_actions(level: str, lang: str = "en") -> List[str]:
    """
    Returns ordered tiered civil actions corresponding to the risk severity.
    - Low: Stage 1
    - Medium: Stage 1 + Stage 2
    - High: Stage 1 + Stage 2 + Stage 3
    """
    lvl = str(level).strip().lower()
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"

    stages = ["Stage 1"]
    if lvl in ("medium", "moderate"):
        stages = ["Stage 1", "Stage 2"]
    elif lvl in ("high", "severe"):
        stages = ["Stage 1", "Stage 2", "Stage 3"]

    return [TIERED_CIVIL_ACTIONS[s].get(lang_key, TIERED_CIVIL_ACTIONS[s]["en"]) for s in stages]


def format_whatsapp_broadcast(
    district: str,
    hazard: str,
    level: str,
    lang: str = "en",
    hours: int = 72,
    driver_summary: Optional[str] = None,
) -> str:
    """
    Builds the official WhatsApp emergency broadcast text payload
    with tiered civil actions, TreeSHAP driver insight, and native PRO disclaimer.
    """
    lang_key = lang.lower() if lang.lower() in ("en", "te", "hi") else "en"
    alert_body = get_alert(hazard, level, lang_key, district, hours)
    actions = get_tiered_civil_actions(level, lang_key)

    header_map = {
        "en": f"🚨 *JALDRISHTI EMERGENCY DISPATCH — {district.upper()}*",
        "te": f"🚨 *జలదృష్టి అత్యవసర సమాచారం — {district.upper()}*",
        "hi": f"🚨 *जलदृष्टि आपातकालीन बुलेटिन — {district.upper()}*",
    }
    actions_header_map = {
        "en": "📋 *Mandatory Civil Defense Actions:*",
        "te": "📋 *తప్పనిసరిగా తీసుకోవలసిన చర్యలు:*",
        "hi": "📋 *अनिवार्य नागरिक सुरक्षा उपाय:*",
    }
    driver_header_map = {
        "en": "🧠 *Key Hydro-Driver (TreeSHAP):*",
        "te": "🧠 *ప్రధాన హైడ్రలాజికల్ కారణం (TreeSHAP):*",
        "hi": "🧠 *प्रमुख हाइड्रोलॉजिकल कारक (TreeSHAP):*",
    }

    lines = [
        header_map.get(lang_key, header_map["en"]),
        f"⏱️ Horizon: {hours}h | Severity: {str(level).upper()}",
        "",
        alert_body,
    ]

    if driver_summary:
        lines.append("")
        lines.append(driver_header_map.get(lang_key, driver_header_map["en"]))
        lines.append(f"• {driver_summary}")

    lines.append("")
    lines.append(actions_header_map.get(lang_key, actions_header_map["en"]))
    for act in actions:
        lines.append(f"• {act}")

    lines.append("")
    lines.append(DISCLAIMER_TAG)

    return "\n".join(lines)
