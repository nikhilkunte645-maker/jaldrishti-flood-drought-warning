"""
JalDrishti - Phase 5: Multilingual Warning Generator
Generates localized, clear, and actionable emergency alerts in English, Telugu, and Hindi.
Placeholders: {district}, {hours}.
"""

from typing import Dict, Optional

# ==============================================================================
# MULTILINGUAL ALERT TEMPLATES
# NOTE: English is primary. Telugu and Hindi translations are provided for
# hyper-local grassroots communication.
# ==============================================================================

# NEEDS NATIVE REVIEW
ALERTS: Dict[str, Dict[str, Dict[str, str]]] = {
    "flood": {
        "Low": {
            "en": "Normal conditions in {district}. No flood threat expected within next {hours} hours. Rivers flowing within safe banks.",
            "te": "{district} లో సాధారణ పరిస్థితులు ఉన్నాయి. రాబోయే {hours} గంటల్లో వరద ముప్పు లేదు. నదులు సురక్షిత పరిమితుల్లో ప్రవహిస్తున్నాయి.",
            "hi": "{district} में स्थिति सामान्य है। अगले {hours} घंटों में बाढ़ का कोई खतरा नहीं है। नदियां सुरक्षित स्तर पर बह रही हैं.",
        },
        "Medium": {
            "en": "Flood Advisory: Rising water levels in {district}. Moderate flood risk within {hours} hours. Farmers and riverside residents should stay alert.",
            "te": "వరద హెచ్చరిక: {district} లో నదీ ప్రవాహాలు పెరుగుతున్నాయి. రాబోయే {hours} గంటల్లో మోస్తరు వరద ముప్పు ఉంది. నదీ పరీవాహక ప్రాంత ప్రజలు అప్రమత్తంగా ఉండాలి.",
            "hi": "बाढ़ चेतावनी: {district} में जलस्तर बढ़ रहा है। अगले {hours} घंटों में मध्यम बाढ़ का खतरा है। नदी किनारे रहने वाले लोग सतर्क रहें।",
        },
        "High": {
            "en": "CRITICAL FLOOD WARNING for {district}! High risk of inundation within next {hours} hours. Move to higher ground immediately and follow disaster response orders.",
            "te": "తీవ్ర వరద హెచ్చరిక! {district} లో రాబోయే {hours} గంటల్లో తీవ్ర వరద ముప్పు ఉంది. తక్షణమే సురక్షిత ఎత్తైన ప్రదేశాలకు చేరుకోండి మరియు అధికారుల సూచనలు పాటించండి.",
            "hi": "गंभीर बाढ़ चेतावनी! {district} में अगले {hours} घंटों में भीषण बाढ़ का खतरा है। तुरंत ऊंचे सुरक्षित स्थानों पर जाएं और आपदा प्रबंधन के निर्देशों का पालन करें।",
        },
    },
    "drought": {
        "Low": {
            "en": "Moisture levels in {district} are normal. No immediate drought stress detected. Agricultural conditions stable.",
            "te": "{district} లో నేల తేమ మరియు వర్షపాతం సాధారణ స్థాయిలో ఉన్నాయి. ఎటువంటి కరువు ముప్పు లేదు.",
            "hi": "{district} में नमी और वर्षा का स्तर सामान्य है। सूखे का कोई तत्काल खतरा नहीं है।",
        },
        "Medium": {
            "en": "Drought Advisory: Moderate moisture deficit in {district}. Conserve irrigation water and monitor standing crops for moisture stress.",
            "te": "కరువు హెచ్చరిక: {district} లో మోస్తరు తేమ కొరత ఉంది. సాగునీటిని పొదుపుగా వాడండి మరియు పంటలను జాగ్రత్తగా గమనించండి.",
            "hi": "सूखा परामर्श: {district} में मध्यम नमी की कमी दर्ज की गई है। सिंचाई के पानी का सावधानी से उपयोग करें।",
        },
        "High": {
            "en": "SEVERE DROUGHT ALERT for {district}! Critical precipitation deficit and depleted soil moisture. Initiate emergency water conservation and crop protection measures.",
            "te": "తీవ్ర కరువు హెచ్చరిక! {district} లో వర్షపాతం మరియు నేల తేమ చాలా తక్కువగా ఉన్నాయి. నీటి సంరక్షణ మరియు పంట రక్షణ చర్యలు వెంటనే చేపట్టండి.",
            "hi": "गंभीर सूखा चेतावनी! {district} में वर्षा की भारी कमी और मिट्टी की नमी का संकट है। आपातकालीन जल संरक्षण उपाय तुरंत शुरू करें।",
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
