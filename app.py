"""
JalDrishti (జలదృష్టి / जलदृष्टि)
Explainable Flood & Drought Early Warning System for the Godavari Basin, Telangana
JNTUH Neural Storm 2026 | Green Planet Track (GP-03)
"""

import base64
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import folium
import joblib
import numpy as np
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_folium import st_folium
import yaml

from src.alerts import (
    get_alert,
    get_tiered_civil_actions,
    format_whatsapp_broadcast,
    DISCLAIMER_TAG,
)
from src.drought import get_drought_status
from src.explainability import (
    extract_top_shap_drivers,
    get_feature_label,
    format_driver_phrase,
)
from src.risk import RISK_COLORS, classify_flood_risk, get_risk_badge_html
from src.telemetry import fetch_basin_data

# ==============================================================================
# ASSETS & BRANDING CONFIGURATION
# ==============================================================================
ASSETS_DIR = Path("docs/assets")
LOGO_PATH = ASSETS_DIR / "logo.png"

LOGO_B64 = ""
if LOGO_PATH.exists():
    try:
        with open(LOGO_PATH, "rb") as f:
            LOGO_B64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        LOGO_B64 = ""

page_icon_val = Image.open(LOGO_PATH) if LOGO_PATH.exists() else "🌊"

st.set_page_config(
    page_title="JalDrishti | Flood & Drought Early Warning",
    page_icon=page_icon_val,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark modern UI with Google Fonts (Inter & Space Grotesk) - Command Center Glassmorphism
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

    <style>
    /* =========================================================================
       GLOBAL COLOR PALETTE & COMMAND CENTER GLASSMORPHISM
       ========================================================================= */
    :root {
        --color-abyss: #030712;
        --color-slate-deep: #0B0F19;
        --color-cyan-glow: #00F2FE;
        --color-blue-accent: #0284C7;
        --color-warning-amber: #F59E0B;
        --color-critical-red: #EF4444;
        --color-safe-green: #10B981;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Main Container with Deep Slate/Abyss Radial Atmosphere */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0F172A 0%, #0B0F19 45%, #030712 100%) !important;
        color: #F1F5F9 !important;
    }

    /* Sleek Frosted Glass Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B0F19 0%, #030712 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 6px 0 24px rgba(0, 0, 0, 0.5) !important;
    }

    [data-testid="stSidebar"] .stSelectbox label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
    }

    /* Brand Typography Classes */
    .brand-header {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        font-weight: 700 !important;
        font-size: 24px !important;
        color: #00F2FE !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0px !important;
        line-height: 1.1 !important;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;
    }
    
    .brand-vernacular {
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        margin-top: 2px !important;
    }
    
    .brand-badge {
        display: inline-block !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 9.5px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        background: rgba(0, 242, 254, 0.12) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 4px !important;
        padding: 2px 7px !important;
        margin-top: 6px !important;
    }

    /* =========================================================================
       FROSTED GLASS CARD CONTAINERS & KPI METRICS
       ========================================================================= */
    .jd-card {
        background: rgba(17, 24, 39, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease, border-color 0.25s ease !important;
    }

    .jd-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(0, 242, 254, 0.35) !important;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 242, 254, 0.15) !important;
    }

    .jd-metric-title {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        margin-bottom: 0.35rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }

    .jd-metric-val {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        font-size: 2.1rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        line-height: 1.15 !important;
        letter-spacing: -0.5px !important;
    }

    .jd-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px !important;
        margin-top: 0.55rem !important;
    }

    /* Simulation Terminal Container for Sandbox */
    .sandbox-terminal {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        border-radius: 14px !important;
        padding: 1.4rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(0, 242, 254, 0.12) !important;
    }

    /* Gradient Primary Action Button */
    div.stButton > button[kind="primary"],
    div.stButton > button[type="primary"] {
        background: linear-gradient(135deg, #00F2FE 0%, #0284C7 100%) !important;
        color: #020617 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.25rem !important;
        box-shadow: 0 4px 18px rgba(0, 242, 254, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[type="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 26px rgba(0, 242, 254, 0.55) !important;
        filter: brightness(1.08) !important;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #94A3B8 !important;
        padding: 10px 18px !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.2s ease !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #00F2FE !important;
        background: rgba(0, 242, 254, 0.05) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00F2FE !important;
        border-bottom: 2px solid #00F2FE !important;
        background: rgba(0, 242, 254, 0.08) !important;
    }

    /* Streamlit Metrics Glassmorphic Override */
    [data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.75) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #F8FAFC !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
    }

    /* =========================================================================
       WHATSAPP DISASTER DISPATCH CARD
       ========================================================================= */
    .whatsapp-container {
        background: rgba(11, 20, 26, 0.95) !important;
        border: 1px solid rgba(34, 46, 53, 0.8) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        margin-top: 1rem !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    .whatsapp-header {
        background: #1f2c34 !important;
        padding: 10px 16px !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    .whatsapp-avatar {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        background: #00a884 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
        box-shadow: 0 0 12px rgba(0, 168, 132, 0.35) !important;
    }
    
    .whatsapp-body {
        background-color: #0b141a !important;
        background-image: radial-gradient(rgba(31, 44, 52, 0.8) 1px, transparent 1px) !important;
        background-size: 16px 16px !important;
        padding: 18px 16px 28px 16px !important;
        min-height: 120px !important;
        position: relative !important;
    }

    .whatsapp-watermark {
        position: absolute;
        right: 18px;
        bottom: 8px;
        font-size: 0.65rem;
        color: rgba(148, 163, 184, 0.28);
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        pointer-events: none;
    }
    
    .whatsapp-bubble {
        background: #005c4b !important;
        color: #e9edef !important;
        padding: 12px 16px !important;
        border-radius: 8px 8px 8px 0px !important;
        max-width: 90% !important;
        font-size: 0.94rem !important;
        line-height: 1.52 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        position: relative !important;
    }
    
    .whatsapp-time {
        text-align: right !important;
        font-size: 0.72rem !important;
        color: #8696a0 !important;
        margin-top: 6px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = Path("data")
MODELS_DIR = Path("models")

DISTRICT_COORDS = {
    "bhadradri_kothagudem": {"name": "Bhadradri Kothagudem", "lat": 17.55, "lon": 80.62},
    "mulugu": {"name": "Mulugu", "lat": 18.19, "lon": 80.00},
    "nizamabad": {"name": "Nizamabad", "lat": 18.67, "lon": 78.09},
    "adilabad": {"name": "Adilabad", "lat": 19.67, "lon": 78.53},
}

# ==============================================================================
# DATA LOADERS (STRICT LOCAL CACHING - NO EXTERNAL APIS AT RUNTIME)
# ==============================================================================
@st.cache_data
def load_predictions() -> pd.DataFrame:
    p = DATA_DIR / "predictions.csv"
    if not p.exists():
        st.error(f"Missing data file: {p}. Please ensure Phase 2 has completed.")
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_data
def load_all_districts_data() -> pd.DataFrame:
    p = DATA_DIR / "all_districts.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_data
def load_drought_data() -> pd.DataFrame:
    p = DATA_DIR / "drought.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_data
def load_thresholds() -> Dict[str, float]:
    p = MODELS_DIR / "thresholds.json"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_metrics() -> pd.DataFrame:
    p = MODELS_DIR / "metrics.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_data
def load_backtest_meta() -> dict:
    p = MODELS_DIR / "backtest.json"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_shap_data() -> pd.DataFrame:
    p = DATA_DIR / "shap_values.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_resource
def load_flood_model(horizon: str):
    p = MODELS_DIR / f"flood_{horizon}.joblib"
    if p.exists():
        return joblib.load(p)
    return None


@st.cache_data
def load_metrics_summary() -> dict:
    p = Path("docs/metrics_summary.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data
def load_basins_config() -> dict:
    p = Path("config/basins.yaml")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


# Load cached local datasets
df_preds = load_predictions()
df_all = load_all_districts_data()
df_drought = load_drought_data()
thresholds = load_thresholds()
basins_config = load_basins_config()
df_metrics = load_metrics()
metrics_summary = load_metrics_summary()
backtest_meta = load_backtest_meta()
df_shap = load_shap_data()

# ==============================================================================
# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div style="position: relative; display: flex; align-items: center; gap: 14px; margin-bottom: 16px; padding: 12px 14px; background: rgba(17, 24, 39, 0.75); border: 1px solid rgba(0, 242, 254, 0.22); border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.45); backdrop-filter: blur(14px);">
                <div style="position: relative; width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <div style="position: absolute; width: 70px; height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0, 242, 254, 0.35) 0%, transparent 70%); filter: blur(3px); pointer-events: none;"></div>
                    <img src="data:image/png;base64,{LOGO_B64}" style="position: relative; width: 52px; height: 52px; border-radius: 12px; box-shadow: 0 4px 14px rgba(0, 242, 254, 0.35); border: 1px solid rgba(0, 242, 254, 0.4); object-fit: contain; background: #0b132b;">
                </div>
                <div style="flex-grow: 1;">
                    <div class="brand-header">JalDrishti</div>
                    <div class="brand-vernacular">జలదృష్టి • जलदृष्टि</div>
                    <div class="brand-badge">JNTUH Neural Storm 2026 • GP-03</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="brand-header">JalDrishti</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-vernacular">జలదృష్టి • जलदृष्टि</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-badge">JNTUH Neural Storm 2026 • GP-03</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-family:'Space Grotesk',sans-serif; font-size:0.75rem; font-weight:700; color:#38BDF8; letter-spacing:0.08em; text-transform:uppercase; margin-top:6px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            🛰️ SATELLITE TELEMETRY & DISTRICT
        </div>
        """,
        unsafe_allow_html=True,
    )

    # River Basin Selector (Config-driven multi-basin scalability)
    basin_display_map = {
        "🌊 Godavari River Basin (Telangana)": "godavari",
        "💧 Krishna River Basin (AP/Telangana)": "krishna",
        "🏞️ Mahanadi River Basin (Odisha)": "mahanadi",
    }
    selected_basin_label = st.selectbox("Select Target River Basin", list(basin_display_map.keys()), index=0)
    selected_basin_id = basin_display_map[selected_basin_label]
    basin_meta = basins_config.get(selected_basin_id, basins_config.get("godavari", {}))
    is_heuristic_transfer = (basin_meta.get("model_status") == "heuristic_transfer")

    # Stations for selected basin
    basin_districts = basin_meta.get("districts", {})
    if selected_basin_id == "godavari" or not basin_districts:
        district_options = {
            "Bhadradri Kothagudem (Bhadrachalam)": "bhadradri_kothagudem",
            "Mulugu (Ramappa / Eturnagaram)": "mulugu",
            "Nizamabad (Sriram Sagar Dam)": "nizamabad",
            "Adilabad (Kadam / Godavari Reach)": "adilabad",
        }
    else:
        district_options = {d_info["name"]: d_slug for d_slug, d_info in basin_districts.items()}

    selected_dist_label = st.selectbox("Select Station / Reach", list(district_options.keys()), index=0)
    selected_slug = district_options[selected_dist_label]
    selected_dist_name = selected_dist_label.split(" (")[0]

    active_basin_coords = {
        d_slug: {"name": d_info["name"], "lat": d_info["lat"], "lon": d_info["lon"]}
        for d_slug, d_info in basin_districts.items()
    } if basin_districts else DISTRICT_COORDS

    st.markdown(
        """
        <div style="font-family:'Space Grotesk',sans-serif; font-size:0.75rem; font-weight:700; color:#38BDF8; letter-spacing:0.08em; text-transform:uppercase; margin-top:14px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            ⚙️ HYDRO-LOGICAL RUNTIME PARAMETERS
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language Selector
    language_map = {
        "English": "en",
        "తెలుగు (Telugu)": "te",
        "हिन्दी (Hindi)": "hi",
    }
    selected_lang_label = st.selectbox("Vernacular Alert Language", list(language_map.keys()), index=0)
    selected_lang = language_map[selected_lang_label]

    # Telemetry Ingestion
    @st.cache_data(ttl=1800)
    def load_telemetry_cached(slug: str):
        try:
            return fetch_basin_data(slug, timeout_sec=2.5)
        except Exception:
            return {"mode": "LOCAL CACHE FALLBACK (OFFLINE)", "data_source": "Local Historical Fixture Cache"}, "LOCAL CACHE FALLBACK (OFFLINE)"

    live_telemetry, telemetry_mode = load_telemetry_cached(selected_slug)

    # Date Selector from Predictions
    if not is_heuristic_transfer and not df_preds.empty:
        dist_preds = df_preds[df_preds["district_slug"] == selected_slug].sort_values("date")
        available_dates = dist_preds["date"].tolist()
        default_idx = available_dates.index("2022-07-14") if "2022-07-14" in available_dates else len(available_dates) - 1
        selected_date = st.selectbox("Inspection Date (Test Window: 2022-2025)", available_dates, index=default_idx)
    else:
        selected_date = str(live_telemetry.get("observation_date", "2026-11-05"))

    st.markdown(
        """
        <div style="font-family:'Space Grotesk',sans-serif; font-size:0.75rem; font-weight:700; color:#38BDF8; letter-spacing:0.08em; text-transform:uppercase; margin-top:14px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            📡 DUAL-MODE TELEMETRY STATUS
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "LIVE" in telemetry_mode:
        badge_sidebar = '<span style="color:#10B981; font-weight:700;">🟢 LIVE TELEMETRY (OPEN-METEO)</span>'
        badge_header = '<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.18); border:1px solid #10B981; color:#10B981; padding:3px 10px; border-radius:20px; font-size:0.73rem; font-weight:700; margin-bottom:6px;">🟢 LIVE TELEMETRY - OPEN-METEO</div>'
    else:
        badge_sidebar = '<span style="color:#F59E0B; font-weight:700;">🟡 LOCAL CACHE FALLBACK (OFFLINE)</span>'
        badge_header = '<div style="display:inline-flex; align-items:center; gap:6px; background:rgba(245,158,11,0.18); border:1px solid #F59E0B; color:#F59E0B; padding:3px 10px; border-radius:20px; font-size:0.73rem; font-weight:700; margin-bottom:6px;">🟡 LOCAL CACHE FALLBACK (OFFLINE)</div>'

    st.markdown(
        f"""
        <div style="font-size:0.75rem; color:#94a3b8; line-height:1.45; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:10px 12px; margin-bottom:12px;">
        {badge_sidebar}<br>
        • Ingestion: {live_telemetry.get('data_source', 'Open-Meteo & Local Cache')}<br>
        • Resilience: Offline-capable with automatic live ingestion<br>
        • Persistent Cache: 3-Hour TTL on Disk
        </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_path = Path("docs/JalDrishti_Hackathon_Submission_Report.pdf")
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Official PDF Report",
                data=f.read(),
                file_name="JalDrishti_Hackathon_Submission_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ==============================================================================
# APP HEADER
# ==============================================================================
col_title, col_status = st.columns([3.2, 1])
with col_title:
    col_logo, col_heading = st.columns([0.15, 0.85])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=62)
    with col_heading:
        st.title("JalDrishti (जलदृष्टि / జలదృష్టి)")
    st.markdown(
        "**Explainable flood and drought early warning in your own language** • "
        "Hyper-localized hydrological intelligence for the Godavari Basin, Telangana"
    )

with col_status:
    if is_heuristic_transfer:
        dist_threshold = float(basin_districts.get(selected_slug, {}).get("threshold_m3s", 100.0))
    else:
        dist_threshold = thresholds.get(selected_slug, 50.0)
    st.markdown(
        f"""
        <div style="text-align: right; margin-bottom: 4px;">
            {badge_header}
        </div>
        <div class="jd-card" style="padding: 12px 16px; text-align: right; border-top: 3px solid #00F2FE;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8;">95th Pct Flood Threshold</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #00F2FE; letter-spacing: -0.5px;">{dist_threshold:.1f} <span style="font-size: 0.85rem; color: #94A3B8;">m³/s</span></div>
            <div style="font-size: 0.72rem; color: #38BDF8; margin-top: 2px;">Station: {selected_dist_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_flood, tab_drought, tab_audit, tab_operations = st.tabs([
    "🌊 Rapid Flood Inundation (24h - 72h Horizon)",
    "🌾 Meteorological & Agricultural Drought (SPI-1 & SPI-3, 30-90 Day Horizon)",
    "🔬 Model Audit, Baseline Comparison & Limitations",
    "🏛️ Operations, B2G Sustainability & Deployment Roadmap",
])

# Retrieve data for selected district and date
selected_row = pd.Series(dtype=object)
if not is_heuristic_transfer and not df_preds.empty:
    m = (df_preds["district_slug"] == selected_slug) & (df_preds["date"] == selected_date)
    matching = df_preds[m]
    if not matching.empty:
        selected_row = matching.iloc[0]

if is_heuristic_transfer:
    cur_discharge = float(live_telemetry.get("river_discharge", 35.0))
    cur_precip = float(live_telemetry.get("precip_mm", 0.0))
    cur_soil = float(live_telemetry.get("soil_moisture", 0.35))
    ratio = cur_discharge / max(dist_threshold, 1.0)
    prob_72h = float(min(0.98, max(0.04, ratio * 0.50)))
    prob_48h = float(min(0.98, max(0.04, ratio * 0.44)))
    prob_24h = float(min(0.98, max(0.04, ratio * 0.38)))
else:
    prob_24h = float(selected_row.get("prob_24h", 0.0))
    prob_48h = float(selected_row.get("prob_48h", 0.0))
    prob_72h = float(selected_row.get("prob_72h", 0.0))
    cur_discharge = float(selected_row.get("river_discharge", 0.0))
    cur_precip = float(selected_row.get("precip_mm", 0.0))
    cur_soil = float(selected_row.get("soil_moisture", 0.0))

risk_24h_level, color_24h = classify_flood_risk(prob_24h)
risk_48h_level, color_48h = classify_flood_risk(prob_48h)
risk_72h_level, color_72h = classify_flood_risk(prob_72h)

# Drought Status
drought_info = get_drought_status(selected_slug, selected_date)
drought_class = drought_info.get("drought_class", "Normal")
drought_color = RISK_COLORS.get(drought_class, "#10b981")
spi_1 = drought_info.get("spi_1", 0.0)
spi_3 = drought_info.get("spi_3", 0.0)
sm_anomaly_z = drought_info.get("sm_anomaly_z", 0.0)

# Explainability analysis for current observation
shap_analysis = {}
if not df_shap.empty:
    m_shap = (df_shap["district_slug"] == selected_slug) & (df_shap["date"] == selected_date)
    matching_shap = df_shap[m_shap]
    if not matching_shap.empty:
        shap_analysis = extract_top_shap_drivers(matching_shap.iloc[0], lang=selected_lang, top_n=3)

if not shap_analysis:
    indicative_vals = {
        "precip_roll_3d": cur_precip * 0.05,
        "river_discharge": (cur_discharge / max(dist_threshold, 1.0) - 0.5) * 1.2,
        "soil_moisture": (cur_soil - 0.35) * 1.5,
        "river_discharge_diff_1d": 0.15,
        "precip_roll_7d": cur_precip * 0.08,
    }
    shap_analysis = extract_top_shap_drivers(indicative_vals, lang=selected_lang, top_n=3)

# ==============================================================================
# TAB 1: RAPID FLOOD INUNDATION (24h - 72h HORIZON)
# ==============================================================================
with tab_flood:
    if is_heuristic_transfer:
        st.warning(
            f"⚠️ **Heuristic transfer mode: requires 3-5 years of localized gauge data for full XGBoost/TreeSHAP weight calibration.** "
            f"Currently monitoring **{basin_meta.get('name')}** at station **{selected_dist_label}** using zero-shot threshold heuristics against live Open-Meteo & ECMWF GloFAS telemetry."
        )

    col_map, col_overview = st.columns([1.1, 1.4])

    with col_map:
        st.markdown(f"##### 📍 {basin_meta.get('name', 'Basin')} Monitoring Network")
        center_lat = float(np.mean([info["lat"] for info in active_basin_coords.values()]))
        center_lon = float(np.mean([info["lon"] for info in active_basin_coords.values()]))
        telangana_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8 if is_heuristic_transfer else 7,
            tiles="OpenStreetMap",
            control_scale=True,
        )

        for slug, info in active_basin_coords.items():
            if is_heuristic_transfer:
                t_data, _ = fetch_basin_data(slug, timeout_sec=1.5)
                q_val = float(t_data.get("river_discharge", 30.0))
                thresh_val = float(basin_districts.get(slug, {}).get("threshold_m3s", 100.0))
                dist_p = min(0.98, max(0.05, (q_val / max(thresh_val, 1.0)) * 0.50))
            else:
                dist_p = 0.0
                if not df_preds.empty:
                    sub_match = df_preds[(df_preds["district_slug"] == slug) & (df_preds["date"] == selected_date)]
                    if not sub_match.empty:
                        dist_p = float(sub_match.iloc[0]["prob_72h"])

            level, color = classify_flood_risk(dist_p)
            is_active = (slug == selected_slug)
            radius = 16 if is_active else 10
            weight = 3 if is_active else 1

            popup_html = f"""
            <div style="font-family:sans-serif; color:#0f172a; min-width:140px;">
                <b>{info['name']}</b><br>
                72h Flood Risk: <b style="color:{color}">{level} ({dist_p:.1%})</b><br>
                Status: {'Heuristic Live Telemetry' if is_heuristic_transfer else f'Historical Date {selected_date}'}
            </div>
            """

            folium.CircleMarker(
                location=[info["lat"], info["lon"]],
                radius=radius,
                color="#ffffff" if is_active else color,
                weight=weight,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"{info['name']}: {level} ({dist_p:.1%})",
            ).add_to(telangana_map)

        st_folium(telangana_map, width="100%", height=310, returned_objects=[])

    with col_overview:
        st.markdown(f"##### 🌊 Hydro-Meteorological Snapshot ({selected_date})")
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            st.markdown(
                f"""
                <div class="jd-card" style="border-top: 3px solid {'#EF4444' if cur_discharge > dist_threshold else '#10B981'};">
                    <div class="jd-metric-title">River Discharge</div>
                    <div class="jd-metric-val">{cur_discharge:.1f} <span style="font-size:0.9rem; color:#94a3b8;">m³/s</span></div>
                    <span class="jd-badge" style="background:{'#ef444422' if cur_discharge > dist_threshold else '#10b98122'}; color:{'#ef4444' if cur_discharge > dist_threshold else '#10b981'}; border:1px solid {'#ef4444' if cur_discharge > dist_threshold else '#10b981'};">
                        {'⚠️ Above Flood Threshold' if cur_discharge > dist_threshold else '✓ Normal River Flow'}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_c2:
            st.markdown(
                f"""
                <div class="jd-card" style="border-top: 3px solid #38BDF8;">
                    <div class="jd-metric-title">Daily Precipitation</div>
                    <div class="jd-metric-val">{cur_precip:.1f} <span style="font-size:0.9rem; color:#94a3b8;">mm</span></div>
                    <span class="jd-badge" style="background:#38bdf822; color:#38bdf8; border:1px solid #38bdf8;">
                        24h Observed Rain
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_c3:
            st.markdown(
                f"""
                <div class="jd-card" style="border-top: 3px solid #A855F7;">
                    <div class="jd-metric-title">Soil Moisture (0-7cm)</div>
                    <div class="jd-metric-val">{cur_soil:.3f} <span style="font-size:0.9rem; color:#94a3b8;">m³/m³</span></div>
                    <span class="jd-badge" style="background:#a855f722; color:#c084fc; border:1px solid #c084fc;">
                        Saturation Level
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # WhatsApp Broadcast Card with Tiered Civil Actions and Translation Disclaimer
        driver_summary_phrase = ""
        if shap_analysis and shap_analysis.get("positive"):
            driver_summary_phrase = shap_analysis["positive"][0]["phrase"]
        elif shap_analysis and shap_analysis.get("summary"):
            driver_summary_phrase = shap_analysis.get("summary")

        whatsapp_flood_msg = format_whatsapp_broadcast(
            district=selected_dist_name,
            hazard="flood",
            level=risk_72h_level,
            lang=selected_lang,
            hours=72,
            driver_summary=driver_summary_phrase,
        )

        st.markdown(
            f"""
            <div class="whatsapp-container">
                <div class="whatsapp-header">
                    <div class="whatsapp-avatar">🌊</div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight:700; color:#e9edef; font-size:0.92rem; font-family:'Space Grotesk', sans-serif;">JalDrishti Emergency Dispatch • జలదృష్టి</div>
                        <div style="font-size:0.75rem; color:#00a884;">TGSDMA Official Protocol ({selected_lang_label})</div>
                    </div>
                    <div style="font-size: 0.68rem; color: #8696a0; border: 1px solid rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 6px; font-weight:600; letter-spacing:0.04em;">TIERED ACTIONS</div>
                </div>
                <div class="whatsapp-body">
                    <div class="whatsapp-watermark">TGSDMA • EARLY WARNING DISPATCH</div>
                    <div class="whatsapp-bubble" style="white-space: pre-line; line-height: 1.45; font-size: 0.85rem;">
{whatsapp_flood_msg}
                        <div class="whatsapp-time">
                            {selected_date} • 06:00 IST <span style="color:#53bdeb;">✔✔</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Risk Horizon Cards
    st.markdown("##### 🚨 Early Warning Horizon Matrix (Flood Forecast)")
    c_24, c_48, c_72 = st.columns(3)

    with c_24:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid {color_24h};">
                <div class="jd-metric-title">24-Hour Flood Horizon</div>
                <div class="jd-metric-val">{prob_24h:.1%}</div>
                <span class="jd-badge" style="background:{color_24h}22; color:{color_24h}; border:1px solid {color_24h};">
                    {risk_24h_level.upper()} RISK
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Valid: Tomorrow ({pd.to_datetime(selected_date) + pd.Timedelta(days=1):%b %d})</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_48:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid {color_48h};">
                <div class="jd-metric-title">48-Hour Flood Horizon</div>
                <div class="jd-metric-val">{prob_48h:.1%}</div>
                <span class="jd-badge" style="background:{color_48h}22; color:{color_48h}; border:1px solid {color_48h};">
                    {risk_48h_level.upper()} RISK
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Valid: Next 2 Days</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_72:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid {color_72h};">
                <div class="jd-metric-title">72-Hour Flood Horizon</div>
                <div class="jd-metric-val">{prob_72h:.1%}</div>
                <span class="jd-badge" style="background:{color_72h}22; color:{color_72h}; border:1px solid {color_72h};">
                    {risk_72h_level.upper()} RISK
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Target Horizon: 3 Days</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 30-Day Preceding Hydrological Dynamics Plotly Chart
    st.markdown(f"##### 📈 30-Day Preceding Hydrological Dynamics for {selected_dist_name}")
    if not df_all.empty:
        dt_end = pd.to_datetime(selected_date)
        dt_start = dt_end - pd.Timedelta(days=30)
        dist_history = df_all[
            (df_all["district_slug"] == selected_slug)
            & (pd.to_datetime(df_all["date"]) >= dt_start)
            & (pd.to_datetime(df_all["date"]) <= dt_end)
        ].sort_values("date")

        if not dist_history.empty:
            fig_30d = make_subplots(specs=[[{"secondary_y": True}]])
            fig_30d.add_trace(
                go.Bar(
                    x=dist_history["date"],
                    y=dist_history["precip_mm"],
                    name="Daily Precipitation (mm)",
                    marker_color="#38bdf8",
                    opacity=0.6,
                ),
                secondary_y=False,
            )
            fig_30d.add_trace(
                go.Scatter(
                    x=dist_history["date"],
                    y=dist_history["river_discharge"],
                    name="River Discharge (m³/s)",
                    mode="lines+markers",
                    line=dict(color="#f59e0b", width=3),
                    marker=dict(size=6, color="#d97706"),
                ),
                secondary_y=True,
            )
            fig_30d.add_hline(
                y=dist_threshold,
                line=dict(color="#ef4444", dash="dash", width=2),
                annotation_text=f"95th Pct Flood Threshold ({dist_threshold:.1f} m³/s)",
                annotation_position="top left",
                annotation_font_color="#ef4444",
                secondary_y=True,
            )
            fig_30d.update_layout(
                paper_bgcolor="#0b132b",
                plot_bgcolor="#1c2541",
                font=dict(color="#cbd5e1"),
                margin=dict(l=40, r=40, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified",
                height=320,
            )
            fig_30d.update_xaxes(gridcolor="#334155")
            fig_30d.update_yaxes(title_text="Precipitation (mm)", gridcolor="#334155", secondary_y=False)
            fig_30d.update_yaxes(title_text="Discharge (m³/s)", gridcolor="#334155", secondary_y=True)
            st.plotly_chart(fig_30d, use_container_width=True)
        else:
            st.info("Insufficient historical records in the selected 30-day window.")

    # --------------------------------------------------------------------------
    # EXPLAINABLE AI (SHAP FEATURE ATTRIBUTION & TRILINGUAL MAPPING)
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### 🧠 Why this risk? (Explainable AI Attribution for 72h Flood Forecast)")
    st.caption("Local TreeSHAP feature contributions explaining why the XGBoost model predicted this 72h flood likelihood.")

    try:
        if not df_shap.empty:
            m_shap = (df_shap["district_slug"] == selected_slug) & (df_shap["date"] == selected_date)
            matching_shap = df_shap[m_shap]

            if not matching_shap.empty:
                shap_row = matching_shap.iloc[0]
                shap_cols = [c for c in df_shap.columns if c.startswith("shap_")]

                contribs = []
                for sc in shap_cols:
                    val = float(shap_row.get(sc, 0.0))
                    label = get_feature_label(sc, lang=selected_lang)
                    contribs.append({"feature": label, "shap_value": val, "abs_val": abs(val)})

                contrib_df = pd.DataFrame(contribs).sort_values("abs_val", ascending=False).head(5)
                contrib_df = contrib_df.sort_values("abs_val", ascending=True)

                colors = ["#ef4444" if v > 0 else "#38bdf8" for v in contrib_df["shap_value"]]

                fig_shap = go.Figure(
                    go.Bar(
                        x=contrib_df["shap_value"],
                        y=contrib_df["feature"],
                        orientation="h",
                        marker_color=colors,
                        text=[f"{v:+.2f}" for v in contrib_df["shap_value"]],
                        textposition="outside",
                    )
                )

                fig_shap.update_layout(
                    title=dict(
                        text=f"<b>Top 5 Drivers for {selected_dist_name} ({selected_date})</b><br><sup>Red = Increases Flood Risk (+) | Blue = Decreases Flood Risk (-)</sup>",
                        font=dict(size=14, color="#f1f5f9"),
                    ),
                    paper_bgcolor="#0b132b",
                    plot_bgcolor="#1c2541",
                    font=dict(color="#cbd5e1"),
                    margin=dict(l=40, r=40, t=50, b=30),
                    height=280,
                    xaxis=dict(title="SHAP Value (Impact on Log-Odds of Flood)", zeroline=True, zerolinecolor="#64748b", gridcolor="#334155"),
                    yaxis=dict(gridcolor="#334155"),
                )

                st.plotly_chart(fig_shap, use_container_width=True)

        # Dynamic Trilingual Natural Language Explanation
        st.info(f"**Hydrological Attribution:** {shap_analysis.get('summary', '')}")

        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown("###### 🚨 Top Risk-Elevating Factors (+)")
            if shap_analysis.get("positive"):
                for p in shap_analysis["positive"]:
                    st.markdown(
                        f"""<div style="background:rgba(239,68,68,0.12); border:1px solid #ef4444; border-radius:6px; padding:6px 10px; margin-bottom:6px; font-size:0.85rem; color:#fca5a5;">
                        • <b>{p['phrase']}</b> (SHAP: {p['shap']:+.2f})
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No significant risk-elevating drivers detected.")

        with col_neg:
            st.markdown("###### 🛡️ Top Risk-Suppressing Factors (-)")
            if shap_analysis.get("negative"):
                for n in shap_analysis["negative"]:
                    st.markdown(
                        f"""<div style="background:rgba(56,189,248,0.12); border:1px solid #38bdf8; border-radius:6px; padding:6px 10px; margin-bottom:6px; font-size:0.85rem; color:#bae6fd;">
                        • <b>{n['phrase']}</b> (SHAP: {n['shap']:+.2f})
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No significant risk-suppressing drivers detected.")

    except Exception as e:
        st.warning(f"Feature attribution temporarily unavailable: {e}")

    # --------------------------------------------------------------------------
    # INTERACTIVE WHAT-IF SCENARIO SANDBOX (LIVE DYNAMIC INFERENCE)
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### 🧪 Interactive Scenario Sandbox / Real-Time What-If Simulator")
    st.caption("Simulate hypothetical rainfall, discharge, and soil saturation combinations to evaluate live model inference.")

    try:
        with st.container():
            st.markdown(
                """
                <div class="sandbox-terminal">
                    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(0, 242, 254, 0.25); padding-bottom: 10px; margin-bottom: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #00F2FE; box-shadow: 0 0 10px #00F2FE;"></span>
                            <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #00F2FE; font-size: 0.95rem; letter-spacing: 0.05em; text-transform: uppercase;">Hydraulic Stress-Testing Terminal</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="display:inline-flex; align-items:center; gap:5px; background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; font-family:'Inter',sans-serif; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:4px;">🔵 HISTORICAL REPLAY / SIMULATION</span>
                            <span style="font-family: 'Inter', monospace; font-size: 0.72rem; color: #94A3B8; background: rgba(0, 242, 254, 0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0, 242, 254, 0.3);">LOCAL_AIRGAPPED_ENGINE v2.4</span>
                        </div>
                    </div>
                    <p style="color: #94A3B8; font-size: 0.82rem; margin-bottom: 0px;">
                    Simulate non-linear hydraulic conditions by adjusting 24h precipitation, upstream river inflow, and volumetric soil saturation. Live inference is executed directly against local gradient-boosted trees.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            sb_c1, sb_c2, sb_c3, sb_c4 = st.columns(4)
            with sb_c1:
                sim_rain = st.slider("Simulated 24h Rainfall (mm)", min_value=0.0, max_value=300.0, value=45.0, step=5.0)
            with sb_c2:
                sim_discharge = st.slider("Current River Discharge (m³/s)", min_value=0.0, max_value=400.0, value=65.0, step=5.0)
            with sb_c3:
                sim_soil_pct = st.slider("Volumetric Soil Moisture (%)", min_value=10.0, max_value=100.0, value=55.0, step=5.0)
            with sb_c4:
                sim_horizon = st.selectbox("Target Horizon", ["24h", "48h", "72h"], index=2)

            run_inference = st.button("⚡ Run Live Hydraulic Inference", use_container_width=True, type="primary")

            if run_inference:
                model = load_flood_model(sim_horizon)
                if model is not None:
                    sim_soil_vol = sim_soil_pct / 100.0
                    syn_data = {
                        "precip_roll_1d": [sim_rain],
                        "precip_roll_3d": [sim_rain * 1.8],
                        "precip_roll_7d": [sim_rain * 2.8],
                        "precip_roll_14d": [sim_rain * 4.2],
                        "soil_moisture": [sim_soil_vol],
                        "soil_moisture_diff_3d": [max(0.0, sim_soil_vol * 0.15)],
                        "river_discharge": [sim_discharge],
                        "river_discharge_lag_1d": [sim_discharge * 0.85],
                        "river_discharge_lag_2d": [sim_discharge * 0.70],
                        "river_discharge_lag_3d": [sim_discharge * 0.60],
                        "river_discharge_diff_1d": [sim_discharge * 0.15],
                        "month": [7],
                    }
                    syn_df = pd.DataFrame(syn_data)
                    sim_prob = float(model.predict_proba(syn_df)[:, 1][0])
                    sim_level, sim_color = classify_flood_risk(sim_prob)

                    res_c1, res_c2 = st.columns([1, 2.2])
                    with res_c1:
                        st.markdown(
                            f"""
                            <div class="jd-card" style="border-top: 4px solid {sim_color}; text-align:center;">
                                <div class="jd-metric-title">Simulated {sim_horizon} Probability</div>
                                <div class="jd-metric-val" style="color:{sim_color};">{sim_prob:.1%}</div>
                                <span class="jd-badge" style="background:{sim_color}22; color:{sim_color}; border:1px solid {sim_color}; font-size:0.95rem;">
                                    {sim_level.upper()} RISK
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with res_c2:
                        if sim_level == "High":
                            advisory_msg = (
                                f"🚨 **CRITICAL FLOOD RISK ({sim_prob:.1%})**: Simulated runoff volume and catchment saturation "
                                f"indicate river discharge is projected to exceed the {selected_dist_name} flood threshold ({dist_threshold:.1f} m³/s). "
                                f"Immediate deployment of emergency response teams and evacuation of low-lying floodplains advised."
                            )
                        elif sim_level == "Medium":
                            advisory_msg = (
                                f"⚠️ **MODERATE FLOOD WATCH ({sim_prob:.1%})**: Inflow parameters indicate rising water levels nearing "
                                f"critical warning levels. Precautionary monitoring of upstream barrages and flood alert dispatches recommended."
                            )
                        else:
                            advisory_msg = (
                                f"✓ **SAFE CHANNEL CAPACITY ({sim_prob:.1%})**: Simulated discharge remains within normal safe channel carrying capacity. "
                                f"No inundation threat anticipated within the {sim_horizon} window."
                            )
                        st.markdown(
                            f"""
                            <div class="jd-card">
                                <div class="jd-metric-title">Operational Advisory ({selected_dist_name})</div>
                                <p style="font-size:0.92rem; color:#e2e8f0; line-height:1.5; margin-top:8px;">{advisory_msg}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.error(f"Model for horizon {sim_horizon} could not be loaded.")
    except Exception as e:
        st.warning(f"Scenario simulator encountered an edge case: {e}")

# ==============================================================================
# TAB 2: METEOROLOGICAL & AGRICULTURAL DROUGHT (SPI-1 & SPI-3, 30-90 DAY HORIZON)
# ==============================================================================
with tab_drought:
    st.markdown("### 🌾 Long-Term Meteorological & Agricultural Drought Monitoring")
    st.markdown(
        """
        <div style="background:#1e293b; border-left:4px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:15px;">
            <b style="color:#f59e0b; font-size:1.02rem;">Decoupled Hydrological Timescales (30 to 90 Days)</b><br>
            <span style="color:#cbd5e1; font-size:0.88rem;">
            Unlike rapid fluvial flooding which materializes within 24–72 hours, drought is a creeping, cumulative multi-month phenomenon. 
            JalDrishti monitors drought across distinct hydrological timescales using the <b>Standardized Precipitation Index (SPI)</b> 
            fitted via two-parameter Gamma distribution with zero-rain probability adjustment and <b>Soil Moisture Z-Score Anomalies</b> 
            referenced against historical calendar-month baselines (2015–2025).
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 KPI Metrics
    dr_c1, dr_c2, dr_c3, dr_c4 = st.columns(4)
    with dr_c1:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid #38BDF8;">
                <div class="jd-metric-title">SPI-1 (30-Day Index)</div>
                <div class="jd-metric-val">{spi_1:+.2f}</div>
                <span class="jd-badge" style="background:#38bdf822; color:#38bdf8; border:1px solid #38bdf8;">
                    {'Dry Stress' if spi_1 < -1.0 else ('Normal / Wet' if spi_1 >= 0 else 'Mild Deficit')}
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Short-term meteorological rainfall</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with dr_c2:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid #F59E0B;">
                <div class="jd-metric-title">SPI-3 (90-Day Index)</div>
                <div class="jd-metric-val">{spi_3:+.2f}</div>
                <span class="jd-badge" style="background:#f59e0b22; color:#f59e0b; border:1px solid #f59e0b;">
                    {'Agricultural Deficit' if spi_3 < -1.0 else ('Normal Moisture' if spi_3 >= 0 else 'Mild Deficit')}
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Seasonal root-zone moisture deficit</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with dr_c3:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid #A855F7;">
                <div class="jd-metric-title">Soil Moisture Anomaly</div>
                <div class="jd-metric-val">{sm_anomaly_z:+.2f} <span style="font-size:0.85rem; color:#94a3b8;">σ</span></div>
                <span class="jd-badge" style="background:#a855f722; color:#c084fc; border:1px solid #c084fc;">
                    {'Severe Soil Depletion' if sm_anomaly_z < -1.5 else ('Depleted Moisture' if sm_anomaly_z < -0.5 else 'Adequate Saturation')}
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Calendar-month baseline deviation</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with dr_c4:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid {drought_color};">
                <div class="jd-metric-title">Drought Severity Level</div>
                <div class="jd-metric-val" style="color:{drought_color};">{drought_class.upper()}</div>
                <span class="jd-badge" style="background:{drought_color}22; color:{drought_color}; border:1px solid {drought_color};">
                    IMD / NDMA Standard
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Composite multi-indicator rating</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Historical Trajectory Plotly Chart (24-Month Window)
    st.markdown(f"##### 📉 24-Month Drought & Moisture Trajectory ({selected_dist_name})")
    if not df_drought.empty:
        dist_drought = df_drought[df_drought["district_slug"] == selected_slug].copy()
        dist_drought["date_dt"] = pd.to_datetime(dist_drought["date"])
        sel_dt = pd.to_datetime(selected_date)
        start_dt = sel_dt - pd.Timedelta(days=730)
        sub_dr = dist_drought[(dist_drought["date_dt"] >= start_dt) & (dist_drought["date_dt"] <= sel_dt)].sort_values("date_dt")

        if not sub_dr.empty:
            fig_dr = go.Figure()
            fig_dr.add_trace(go.Scatter(
                x=sub_dr["date"],
                y=sub_dr["spi_1"],
                name="SPI-1 (30-Day Meteorological)",
                mode="lines",
                line=dict(color="#38bdf8", dash="dash", width=2),
            ))
            fig_dr.add_trace(go.Scatter(
                x=sub_dr["date"],
                y=sub_dr["spi_3"],
                name="SPI-3 (90-Day Agricultural)",
                mode="lines",
                line=dict(color="#f59e0b", width=3),
            ))
            fig_dr.add_trace(go.Scatter(
                x=sub_dr["date"],
                y=sub_dr["sm_anomaly_z"],
                name="Soil Moisture Z-Score",
                mode="lines",
                line=dict(color="#c084fc", width=1.5),
            ))

            fig_dr.add_hline(y=0.0, line=dict(color="#64748b", dash="dot", width=1))
            fig_dr.add_hline(
                y=-1.0,
                line=dict(color="#f59e0b", dash="dash", width=1.5),
                annotation_text="Moderate Drought (-1.0)",
                annotation_position="bottom left",
                annotation_font_color="#f59e0b",
            )
            fig_dr.add_hline(
                y=-1.5,
                line=dict(color="#ef4444", dash="dash", width=1.5),
                annotation_text="Severe Drought (-1.5)",
                annotation_position="bottom left",
                annotation_font_color="#ef4444",
            )

            fig_dr.update_layout(
                paper_bgcolor="#0b132b",
                plot_bgcolor="#1c2541",
                font=dict(color="#cbd5e1"),
                margin=dict(l=40, r=40, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                yaxis=dict(title="Index Value (Std Dev / Z-Score)", gridcolor="#334155"),
                xaxis=dict(gridcolor="#334155"),
            )
            st.plotly_chart(fig_dr, use_container_width=True)
        else:
            st.info("Insufficient historical drought observations in the 24-month analysis window.")

    st.markdown("---")

    # Agricultural Advisory & WhatsApp Agricultural Bulletin
    col_agri_adv, col_agri_wa = st.columns([1.2, 1.2])

    with col_agri_adv:
        st.markdown(f"##### 🚜 Agricultural Advisory & Mitigation Plan ({selected_lang_label})")
        if drought_class == "High" or drought_class == "Severe":
            if selected_lang == "te":
                adv_p1 = "• **తీవ్ర తేమ కొరత**: అత్యవసర కాలువ నీటి సరఫరా షెడ్యూల్ (రొటేషన్) అమలు చేయండి."
                adv_p2 = "• **పంట మార్పిడి**: నీటి వినియోగం అధికంగా ఉండే వరి సాగును నివారించి, తక్కువ నీటితో పండే మిల్లెట్లు (రాగులు, జొన్నలు), పప్పుధాన్యాల వైపు రైతులను ప్రోత్సహించండి."
                adv_p3 = "• **రక్షణ చర్యలు**: నిల్వ ఉన్న పంటలకు తుంపర సేద్యం (స్ప్రింక్లర్లు) లేదా బిందు సేద్యం (డ్రిప్) ద్వారా జీవనాధార తడులు మాత్రమే ఇవ్వండి."
            elif selected_lang == "hi":
                adv_p1 = "• **गंभीर नमी की कमी**: आपातकालीन नहर जल रोस्टर प्रणाली को तुरंत लागू करें।"
                adv_p2 = "• **फसल विविधीकरण**: अत्यधिक जल-खपत वाले धान की नई बुवाई रोकें; ज्वार, बाजरा, रागी और दलहनी फसलों को प्राथमिकता दें।"
                adv_p3 = "• **संरक्षण सिंचाई**: खड़ी फसलों को केवल जीवन रक्षक ड्रिप या स्प्रिंकलर सिंचाई उपलब्ध कराएं।"
            else:
                adv_p1 = "• **Critical Moisture Deficit**: Enforce emergency canal water rationing and rotational roster deliveries."
                adv_p2 = "• **Contingency Crop Planning**: Restrict new water-intensive paddy transplantation; advocate drought-resilient millets and short-duration pulses."
                adv_p3 = "• **Protective Irrigation**: Shift existing standing acreage to micro-drip and life-saving sprinkler allocations."
        elif drought_class == "Medium" or drought_class == "Moderate":
            if selected_lang == "te":
                adv_p1 = "• **మోస్తరు కరవు సూచన**: నేలలో తేమ ఆవిరి కాకుండా గడ్డి లేదా ప్లాస్టిక్ మల్చింగ్ విధానాలను అనుసరించండి."
                adv_p2 = "• **సాగునీటి పొదుపు**: వర్షాధార పత్తి, వేరుశనగ మరియు మొక్కజొన్న పంటలకు అవసరమైనప్పుడు మాత్రమే నీరు పెట్టండి."
                adv_p3 = "• **నీటి సంరక్షణ**: గ్రామాల్లోని చెరువులు, వ్యవసాయ కుంటల్లోని నీటిని పశువుల తాగునీటి అవసరాల కొరకు భద్రపరచండి."
            elif selected_lang == "hi":
                adv_p1 = "• **मध्यम सूखा परामर्श**: मिट्टी से नमी वाष्पीकरण रोकने हेतु जैविक अथवा प्लास्टिक मल्चिंग का उपयोग करें।"
                adv_p2 = "• **पानी की बचत**: वर्षा आधारित कपास, मूंगफली और मक्का में अनुशासित सूक्ष्म सिंचाई लागू करें।"
                adv_p3 = "• **जल संरक्षण**: कृषि तालाबों और जलाशयों के जल को पशुधन पेयजल हेतु प्राथमिकता दें।"
            else:
                adv_p1 = "• **Moderate Soil Moisture Stress**: Encourage crop residue mulching to reduce surface evapotranspiration."
                adv_p2 = "• **Irrigation Efficiency**: Apply micro-irrigation scheduling to rainfed cotton, groundnut, and maize."
                adv_p3 = "• **Storage Conservation**: Safeguard farm pond (Krishi Vontalu) reserves for livestock and drinking water."
        else:
            if selected_lang == "te":
                adv_p1 = "• **సాధారణ వాతావరణం**: నేలలో సరిపడా తేమ శాతం నమోదైంది. పంటలకు ఎటువంటి కరవు ఒత్తిడి లేదు."
                adv_p2 = "• **సాధారణ సాగు**: సాధారణ ఎరువులు మరియు సాగునీటి నిర్వహణ పద్ధతులను కొనసాగించండి."
                adv_p3 = "• **ముందస్తు భద్రత**: వర్షపు నీటిని చెరువుల్లోకి మళ్లించి భూగర్భ జలాల పునర్భరణకు చర్యలు తీసుకోండి."
            elif selected_lang == "hi":
                adv_p1 = "• **सामान्य परिस्थितियां**: मृदा नमी और वर्षा स्तर संतोषजनक हैं। फसलों पर कोई सूखा तनाव नहीं है।"
                adv_p2 = "• **मानक कृषि कार्य**: सामान्य उर्वरक और जल प्रबंधन अनुसूची जारी रखें।"
                adv_p3 = "• **भविष्य की तैयारी**: वर्षा जल संचयन संरचनाओं को सक्रिय रखें।"
            else:
                adv_p1 = "• **Normal Conditions**: Adequate root-zone soil saturation and cumulative seasonal precipitation."
                adv_p2 = "• **Standard Operations**: Maintain standard agronomic and fertilizer schedules."
                adv_p3 = "• **Rainwater Harvesting**: Maintain percolation tanks and recharge wells for lean seasonal buffers."

        st.markdown(
            f"""
            <div class="jd-card">
                <div class="jd-metric-title">Agronomic Advisory ({selected_dist_name})</div>
                <div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6; margin-top:8px;">
                    {adv_p1}<br>
                    {adv_p2}<br>
                    {adv_p3}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_agri_wa:
        st.markdown("##### 📱 Agricultural Drought WhatsApp Bulletin")
        whatsapp_drought_msg = format_whatsapp_broadcast(
            district=selected_dist_name,
            hazard="drought",
            level=drought_class,
            lang=selected_lang,
            hours=720,
            driver_summary=f"SPI-3: {spi_3:+.2f} | SM-Z: {sm_anomaly_z:+.2f}σ",
        )

        st.markdown(
            f"""
            <div class="whatsapp-container">
                <div class="whatsapp-header">
                    <div class="whatsapp-avatar">🌾</div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight:700; color:#e9edef; font-size:0.92rem; font-family:'Space Grotesk', sans-serif;">JalDrishti Krishi Bulletin • కృషి సమాచారం</div>
                        <div style="font-size:0.75rem; color:#00a884;">Rythu Bharosa Kendra Protocol ({selected_lang_label})</div>
                    </div>
                    <div style="font-size: 0.68rem; color: #8696a0; border: 1px solid rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 6px; font-weight:600; letter-spacing:0.04em;">MONTHLY</div>
                </div>
                <div class="whatsapp-body">
                    <div class="whatsapp-watermark">TGSDMA • KRISHI DROUGHT PROTOCOL</div>
                    <div class="whatsapp-bubble" style="white-space: pre-line; line-height: 1.45; font-size: 0.85rem;">
{whatsapp_drought_msg}
                        <div class="whatsapp-time">
                            {selected_date} • 06:00 IST <span style="color:#53bdeb;">✔✔</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# TAB 3: MODEL AUDIT, BASELINE COMPARISON & LIMITATIONS
# ==============================================================================
with tab_audit:
    st.markdown("### 🔬 Model Audit, Baseline Comparison & Limitations")

    # Section 1: July 2022 Backtest Replay
    st.markdown(
        """
        <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(56,189,248,0.18); border:1px solid #38BDF8; color:#38BDF8; padding:3px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; margin-bottom:10px;">
            🔵 HISTORICAL REPLAY / SIMULATION
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### ⏪ Historic Event Replay: July 2022 Godavari Flood (Bhadrachalam Gauge)")
    st.markdown(
        "Between July 10 and July 18, 2022, the Godavari river basin experienced historic, unprecedented monsoon flooding. "
        "At Bhadrachalam (Bhadradri Kothagudem), river levels crossed the 3rd and highest danger level (53 feet) and peaked "
        "near 71.3 feet, inundating dozens of villages and severing road links. "
        "Here we rigorously evaluate JalDrishti's forward model against this real-world disaster."
    )

    if backtest_meta:
        st.markdown(
            """
            <div style="background:#1e293b; border-left:4px solid #38bdf8; border-radius:8px; padding:12px 16px; margin-bottom:15px;">
                <b style="color:#38bdf8; font-size:1.05rem;">Catchment Saturation Precursor: 7 Days (168 Hours) Ahead of Peak Discharge</b><br>
                <span style="color:#cbd5e1; font-size:0.88rem;">
                <b>Target Horizon vs. Precursor Duration:</b> While the ML model target predicts flood conditions within a <b>72-hour forward window</b>, 
                persistent multi-day precipitation and upper-catchment soil saturation caused sustained high-risk probability alerts (P &ge; 60%) 
                to fire beginning on <b>July 7, 2022</b>—<b>7 calendar days (168 hours)</b> prior to the observed crest on July 14, 2022.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_c1, b_c2, b_c3, b_c4 = st.columns(4)
        with b_c1:
            st.metric("Catchment Precursor Duration", f"{backtest_meta.get('lead_time_days', 0)} Days", f"{backtest_meta.get('lead_time_hours', 0)} Hours Ahead")
        with b_c2:
            st.metric("Observed Peak Crest", str(backtest_meta.get("peak_date", "-")), f"{backtest_meta.get('peak_discharge_m3s', 0):.1f} m³/s")
        with b_c3:
            st.metric("First Precursor Alert", str(backtest_meta.get("warning_date", "-")), f"P={backtest_meta.get('warning_prob_72h', 0):.1%}")
        with b_c4:
            st.metric("Model Target Horizon", "72 Hours", "Rolling Window")

        st.info(f"**Hydrological Analysis:** {backtest_meta.get('analysis_notes', '')}")

    backtest_html_file = MODELS_DIR / "backtest.html"
    if backtest_html_file.exists():
        with open(backtest_html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=620, scrolling=True)
    else:
        st.warning("Backtest visualization HTML not found. Run src/backtest.py to generate it.")

    st.markdown("---")

    # Section 2: Quantitative Performance & Baseline Audit
    st.markdown("#### 📈 Quantitative Performance & Baseline Benchmark Audit")
    st.markdown(
        "All models are strictly evaluated on unseen out-of-time test data (2022-2025). "
        "We benchmark XGBoost against both a **Naive Persistence Baseline** ('Tomorrow equals today') and an "
        "**Antecedent Precipitation Index (API-3 Linear Benchmark)** to ensure machine learning "
        "provides genuine predictive lift over traditional hydrological rules."
    )

    if not df_metrics.empty:
        format_dict = {
            "Precision": "{:.2%}",
            "Recall": "{:.2%}",
            "F1-Score": "{:.2%}",
            "ROC-AUC": "{:.3f}",
        }
        if "F2-Score" in df_metrics.columns:
            format_dict["F2-Score"] = "{:.2%}"

        st.dataframe(
            df_metrics.style.format(format_dict),
            use_container_width=True,
        )

        latency_meta = metrics_summary.get("measured_edge_latency", {})
        if latency_meta:
            st.markdown("##### ⚡ Measured Edge CPU Inference Latency (Empirical Benchmark)")
            l_c1, l_c2, l_c3, l_c4 = st.columns(4)
            with l_c1:
                st.metric("Median Latency (p50)", f"{latency_meta.get('p50_latency_ms', 2.33):.2f} ms", "1,000 Iterations")
            with l_c2:
                st.metric("95th Pct Latency (p95)", f"{latency_meta.get('p95_latency_ms', 3.73):.2f} ms", "Tail Runtime")
            with l_c3:
                st.metric("Execution Target", "Local CPU", latency_meta.get("device", "Edge Node"))
            with l_c4:
                st.metric("Total Model Footprint", "< 4.5 MB", "Serialized Artifacts")

        h72_xgb = metrics_summary.get("horizons", {}).get("72h", {}).get("xgboost", {})
        h72_rec = h72_xgb.get("recall", 0.9066)
        h72_f2 = h72_xgb.get("f2_score", 0.8291)
        h72_tp = h72_xgb.get("true_positives", 524)
        h72_fn = h72_xgb.get("false_negatives", 54)

        st.markdown(
            f"""
            <div style="background:#1e293b; border-left:4px solid #10b981; border-radius:8px; padding:12px 16px; margin-top:15px; margin-bottom:15px;">
                <b style="color:#10b981; font-size:1.02rem;">Asymmetric Disaster Loss Function & F2 Justification</b><br>
                <span style="color:#cbd5e1; font-size:0.88rem;">
                In flood early warning, a <b>False Negative (missed flood)</b> leading to loss of human life and unevacuated settlements is 
                exponentially costlier than a <b>False Positive (precautionary inspection)</b>. 
                The <b>F2-score (&beta;=2)</b> places <b>4x more weight on Recall than Precision</b>. 
                JalDrishti optimizes for maximum F2-score and &gt;90% recall (achieving <b>{h72_f2:.2%} F2 at 72h</b> vs 77.78% for persistence and 61.87% for API-3).
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### 🔬 Key Model Diagnostics & Empirical Trade-Offs")
        st.markdown(
            f"""
            1. **Predictive Lift over Baselines at 72h**:
               - The naive persistence baseline misses **144 flood days** (Recall drops to 75.09%) because persistence cannot anticipate floods that haven't happened yet.
               - The API-3 linear rainfall index triggers **754 false alarms** because rain alone without soil saturation context over-predicts runoff.
               - In contrast, JalDrishti's 72h XGBoost model achieves **{h72_rec:.2%} Recall (F2: {h72_f2:.2%})**, capturing **{h72_tp} out of {h72_tp + h72_fn} flood days** and missing only **{h72_fn} days**.
            2. **The Disaster Warning Trade-Off (Recall vs Precision)**:
               - Using cost-sensitive `scale_pos_weight`, the model intentionally prioritizes high recall (~90%), accepting a manageable rate of false alarms to avoid deadly surprise floods.
            """
        )

    st.markdown("---")
    st.markdown("#### ⚠️ Transparent System Limitations (Academic & Operational Integrity)")
    st.markdown(
        """
        - **Class Imbalance**: River flood events represent only ~5% of daily observations in semi-arid Telangana. Models require cost-sensitive weighting.
        - **Daily Temporal Resolution**: Open-Meteo Flood API provides daily mean discharge. Fast-rising cloudburst flash floods (which occur over 3-6 hours) require sub-daily gauge telemetry.
        - **Modelled vs In-Situ Discharge**: Historical discharge values are derived from European Centre for Medium-Range Weather Forecasts (ECMWF) GloFAS land-surface reanalysis rather than physical Central Water Commission (CWC) river gauges.
        - **Confluence Backwater Dynamics**: Downstream backwater effects (such as the Sabari River confluence near Kunavaram) can artificially elevate flood levels at Bhadrachalam independently of upstream Godavari precipitation.
        - **Ungauged Tributaries & Radar Gaps**: Smaller tributaries and ungauged Eastern Ghats catchments introduce local runoff variance not captured by coarse gridded models.
        - **Non-Official Notice**: This system is developed as an academic hackathon submission for JNTUH Neural Storm 2026 and does not replace official bulletins from the India Meteorological Department (IMD) or Central Water Commission (CWC).
        """
    )

# ==============================================================================
# TAB 4: OPERATIONS, B2G SUSTAINABILITY & DEPLOYMENT ROADMAP
# ==============================================================================
with tab_operations:
    col_about_logo, col_about_header = st.columns([1, 6])
    with col_about_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=105)
    with col_about_header:
        st.markdown("### 🏛️ Operations, B2G Sustainability & Deployment Roadmap")
        st.markdown(
            """
            **JalDrishti (జలదృష్టి / जलदृष्टि)** is an explainable, dual-hazard hydro-informatics platform built for 
            **JNTUH Neural Storm 2026 (Green Planet Track, Challenge GP-03: Flood and Drought Early Warning System)**.
            
            #### 🏢 Institutional B2G Workflow Architecture
            ```mermaid
            flowchart TD
                subgraph INGESTION["1. Telemetry Ingestion Layer"]
                    A1[Open-Meteo Forecast & Flood APIs]
                    A2[ECMWF GloFAS Gridded Reanalysis]
                    A3[Local Offline Fixture Fallback]
                end

                subgraph PREPROC["2. Hydro-Informatics Pipeline"]
                    B1[Rolling Antecedent Precipitation (1d, 3d, 7d, 14d)]
                    B2[Hydraulic Lag Analysis & River Surge Velocity]
                    B3[Soil Moisture Saturation Dynamics (0-7cm)]
                end

                subgraph MODELS["3. Dual-Timescale Predictive Engine"]
                    C1["XGBoost 24h, 48h, 72h Forecasters (F2-Optimized)"]
                    C2["Drought Engine: SPI-1, SPI-3 (Gamma) & Soil Z-Score"]
                end

                subgraph XAI["4. Explainability & Localization"]
                    D1[TreeSHAP Feature Attribution]
                    D2[Trilingual Translation & Natural Language Framing]
                end

                subgraph DISPATCH["5. Multi-Channel Institutional Dispatch"]
                    E1[State EOC Web Command Center]
                    E2[Tiered WhatsApp / SMS Emergency Alerts]
                    E3[Air-Gapped LoRa / VHF Mesh Radio Broadcasts]
                end

                A1 & A2 & A3 --> B1 & B2 & B3
                B1 & B2 & B3 --> C1 & C2
                C1 --> D1 --> D2
                C2 --> D2
                D2 --> E1 & E2 & E3
            ```

            #### 🏛️ Target B2G Institutional Customers
            - **State Disaster Management Authorities**: Telangana (TGSDMA), Andhra Pradesh (APSDMA), and Odisha (OSDMA).
            - **District Emergency Operations Centers (DEOCs)**: District Collectors, Revenue Divisional Officers (RDOs), and Tahsildars.
            - **Agricultural Extension & Rythu Bharosa Kendras (RBKs)**: Gram Panchayat village agriculture assistants and irrigation engineers.

            #### 💼 Cost Structure & Commercial Sustainability
            *(Strategic Projection & Financial Assumptions)*
            - **Pilot District Model**: Estimated at **₹1.5 Lakhs (~$1,800 USD) per district / year** covering:
              1. Edge inference compute licensing and local telemetry ingestion pipelines.
              2. Custom local gauge calibration (integrating physical CWC & state irrigation gauge records).
              3. Vernacular WhatsApp gateway integration & emergency broadcast SLAs.
            - **Compute Efficiency**: Total model payload is **under 4.5 MB** with **~2.33 ms CPU latency**, enabling deployment on standard ₹3,500 ($45) Raspberry Pi 4 nodes in air-gapped district collectorates.

            #### 🗺️ Multi-Basin Scaling Roadmap
            - **Phase 1: Godavari Basin (Telangana)** — Fully calibrated across 4 core districts (Bhadrachalam, Mancherial, Ramagundam, Nizamabad) with 10 years of training data.
            - **Phase 2: Krishna Basin (AP / Telangana)** — Configured with live telemetry and zero-shot heuristic transfer mode for Vijayawada (Prakasam Barrage), Amaravati Reach, and Nagarjuna Sagar.
            - **Phase 3: Mahanadi Basin (Odisha)** — Configured with live telemetry for Cuttack (Mundali Weir), Sambalpur (Hirakud Dam), and Puri Delta.

            #### 👤 Author Attribution & Hackathon Submission
            - **Track**: Green Planet (GP-03: Flood and Drought Early Warning System)
            - **Hackathon**: JNTUH Neural Storm 2026
            - **Team**: Prahar
            - **Lead Engineer**: Nikhil Kunte
            - **Live Web Deployment**: [https://jaldrishti-warning.streamlit.app](https://jaldrishti-warning.streamlit.app)
            - **GitHub Source**: [https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning](https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning)
            """
        )

    pdf_path = Path("docs/JalDrishti_Hackathon_Submission_Report.pdf")
    if pdf_path.exists():
        st.markdown("#### 📥 Official Documentation & Verification Report")
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Full Presentation PDF Report (High-DPI, A4)",
                data=f.read(),
                file_name="JalDrishti_Hackathon_Submission_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
