"""
JalDrishti - Phase 5: Risk Evaluation Engine
Defines operational hazard thresholds, color mappings, and risk tiers.
"""

from typing import Dict, Tuple

# Operational probability thresholds for Flood Early Warning
# Low: < 0.30 (Routine monitoring)
# Medium: 0.30 - 0.60 (Pre-warning / Advisory)
# High: >= 0.60 (Emergency evacuation / Red alert)
RISK_THRESHOLDS = {
    "low_max": 0.30,
    "med_max": 0.60,
}

RISK_COLORS = {
    "Low": "#10b981",       # Emerald Green
    "Medium": "#f59e0b",    # Amber Yellow
    "High": "#ef4444",      # Crimson Red
    "Normal": "#10b981",
    "Moderate": "#f59e0b",
    "Severe": "#ef4444",
}


def classify_flood_risk(prob: float) -> Tuple[str, str]:
    """
    Classify flood probability into Risk Level and Hex Color.
    Returns: (level_name, hex_color)
    """
    if prob < RISK_THRESHOLDS["low_max"]:
        return "Low", RISK_COLORS["Low"]
    elif prob < RISK_THRESHOLDS["med_max"]:
        return "Medium", RISK_COLORS["Medium"]
    else:
        return "High", RISK_COLORS["High"]


def get_risk_badge_html(level: str, prefix: str = "") -> str:
    """Return inline HTML pill/badge for UI display."""
    color = RISK_COLORS.get(level, "#64748b")
    label = f"{prefix} {level}".strip()
    return (
        f'<span style="background-color: {color}22; color: {color}; '
        f'border: 1px solid {color}88; padding: 4px 10px; border-radius: 9999px; '
        f'font-weight: 700; font-size: 0.85rem; letter-spacing: 0.03em;">'
        f'{label}</span>'
    )
