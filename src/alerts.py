"""
JalDrishti - Phase 5 & Upgrade: Multilingual Warning Generator
Generates localized, clear, and actionable emergency alerts in English, Telugu, and Hindi.
Placeholders: {district}, {hours}.
"""

from typing import Dict, Optional

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


def get_alert(
    hazard: str,
    level: str,
    lang: str,
    district: str,
    hours: Optional[int] = 72,
) -> str:
    """
    Retrieve formatted alert message.
    Args:
        hazard: 'flood' or 'drought'
        level: 'Low', 'Medium', 'High' (or 'Normal', 'Moderate', 'Severe' for drought)
        lang: 'en', 'te', or 'hi'
        district: District name string
        hours: Forecast horizon in hours (default 72)
    Returns:
        Formatted text message with no unformatted braces.
    """
    hazard_key = hazard.lower()
    if hazard_key not in ALERTS:
        hazard_key = "flood"

    # Map drought severity names to alert levels if needed
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
