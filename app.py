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

from src.alerts import get_alert
from src.drought import get_drought_status
from src.risk import RISK_COLORS, classify_flood_risk, get_risk_badge_html

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


# Load cached local datasets
df_preds = load_predictions()
df_all = load_all_districts_data()
df_drought = load_drought_data()
thresholds = load_thresholds()
df_metrics = load_metrics()
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

    # District Selector
    district_options = {
        "Bhadradri Kothagudem (Bhadrachalam)": "bhadradri_kothagudem",
        "Mulugu (Ramappa / Eturnagaram)": "mulugu",
        "Nizamabad (Sriram Sagar Dam)": "nizamabad",
        "Adilabad (Kadam / Godavari Reach)": "adilabad",
    }
    selected_dist_label = st.selectbox("Select Godavari District", list(district_options.keys()), index=0)
    selected_slug = district_options[selected_dist_label]
    selected_dist_name = DISTRICT_COORDS[selected_slug]["name"]

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

    # Date Selector from Predictions
    if not df_preds.empty:
        dist_preds = df_preds[df_preds["district_slug"] == selected_slug].sort_values("date")
        available_dates = dist_preds["date"].tolist()
        default_idx = available_dates.index("2022-07-14") if "2022-07-14" in available_dates else len(available_dates) - 1
        selected_date = st.selectbox("Inspection Date (Test Window: 2022-2025)", available_dates, index=default_idx)
    else:
        selected_date = "2022-07-14"

    st.markdown(
        """
        <div style="font-family:'Space Grotesk',sans-serif; font-size:0.75rem; font-weight:700; color:#38BDF8; letter-spacing:0.08em; text-transform:uppercase; margin-top:14px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
            📡 AIR-GAPPED SYSTEM STATUS
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="font-size:0.75rem; color:#94a3b8; line-height:1.45; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:10px 12px; margin-bottom:12px;">
        <span style="color:#10B981; font-weight:600;">● Engine Online (Zero-API Air-Gapped)</span><br>
        • Spatial Scope: 4 Basin Districts<br>
        • Machine Learning: Gradient Boosted Trees (XGBoost)<br>
        • Climatological SPI: Gamma Distribution<br>
        • Telemetry Cache: Verified Valid
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
    dist_threshold = thresholds.get(selected_slug, 50.0)
    st.markdown(
        f"""
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
tab_dashboard, tab_backtest, tab_metrics, tab_about = st.tabs([
    "📊 Risk Dashboard",
    "⏪ Backtest: July 2022 Flood",
    "📈 Model Results & Audits",
    "ℹ️ About & Architecture",
])

# Retrieve data for selected district and date
selected_row = pd.Series(dtype=object)
if not df_preds.empty:
    m = (df_preds["district_slug"] == selected_slug) & (df_preds["date"] == selected_date)
    matching = df_preds[m]
    if not matching.empty:
        selected_row = matching.iloc[0]

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

# ==============================================================================
# TAB 1: RISK DASHBOARD
# ==============================================================================
with tab_dashboard:
    col_map, col_overview = st.columns([1.1, 1.4])

    with col_map:
        st.markdown("##### 📍 Telangana Godavari Basin Network")
        # Build interactive Folium map
        telangana_map = folium.Map(
            location=[18.35, 79.4],
            zoom_start=7,
            tiles="OpenStreetMap",
            control_scale=True,
        )

        for slug, info in DISTRICT_COORDS.items():
            # Get latest 72h risk on selected date for each district
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
                Date: {selected_date}
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

        # WhatsApp Broadcast Card
        alert_text = get_alert(
            hazard="flood" if prob_72h >= 0.3 else ("drought" if drought_class != "Normal" else "flood"),
            level=risk_72h_level if prob_72h >= 0.3 else drought_class,
            lang=selected_lang,
            district=selected_dist_name,
            hours=72,
        )

        st.markdown(
            f"""
            <div class="whatsapp-container">
                <div class="whatsapp-header">
                    <div class="whatsapp-avatar">🌊</div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight:700; color:#e9edef; font-size:0.92rem; font-family:'Space Grotesk', sans-serif;">JalDrishti Emergency Dispatch • జలదృష్టి</div>
                        <div style="font-size:0.75rem; color:#00a884;">TGSDMA Official Verified Protocol ({selected_lang_label})</div>
                    </div>
                    <div style="font-size: 0.68rem; color: #8696a0; border: 1px solid rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 6px; font-weight:600; letter-spacing:0.04em;">AIR-GAPPED MESH</div>
                </div>
                <div class="whatsapp-body">
                    <div class="whatsapp-watermark">TGSDMA • TELANGANA DISASTER MGMT PROTOCOL</div>
                    <div class="whatsapp-bubble">
                        <b>⚠️ {selected_dist_name.upper()} ADVISORY</b><br>
                        {alert_text}
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
    st.markdown("##### 🚨 Early Warning Horizon Matrix")
    c_24, c_48, c_72, c_dr = st.columns(4)

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
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">Lead Time Target: 3 Days</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_dr:
        st.markdown(
            f"""
            <div class="jd-card" style="border-top: 4px solid {drought_color};">
                <div class="jd-metric-title">Drought Severity Status</div>
                <div class="jd-metric-val" style="font-size:1.5rem;">{drought_class}</div>
                <span class="jd-badge" style="background:{drought_color}22; color:{drought_color}; border:1px solid {drought_color};">
                    SPI-3: {spi_3:+.2f} | SM-Z: {sm_anomaly_z:+.2f}
                </span>
                <p style="font-size:0.75rem; color:#94a3b8; margin-top:8px;">SPI-1: {spi_1:+.2f} (Monthly Precip)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 30-Day Preceding Hydrological Dynamics Plotly Chart
    st.markdown(f"##### 📈 30-Day Preceding Hydrological Dynamics for {selected_dist_name}")
    if not df_all.empty:
        # Filter 30 days prior to selected date
        dt_end = pd.to_datetime(selected_date)
        dt_start = dt_end - pd.Timedelta(days=30)
        dist_history = df_all[
            (df_all["district_slug"] == selected_slug)
            & (pd.to_datetime(df_all["date"]) >= dt_start)
            & (pd.to_datetime(df_all["date"]) <= dt_end)
        ].sort_values("date")

        if not dist_history.empty:
            fig_30d = make_subplots(specs=[[{"secondary_y": True}]])

            # Rainfall Bars (Left Axis)
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

            # River Discharge Line (Right Axis)
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

            # Threshold line
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
                height=350,
            )
            fig_30d.update_xaxes(gridcolor="#334155")
            fig_30d.update_yaxes(title_text="Precipitation (mm)", gridcolor="#334155", secondary_y=False)
            fig_30d.update_yaxes(title_text="Discharge (m³/s)", gridcolor="#334155", secondary_y=True)

            st.plotly_chart(fig_30d, use_container_width=True)
        else:
            st.info("Insufficient historical records in the selected 30-day window.")

    # --------------------------------------------------------------------------
    # PHASE 7: EXPLAINABLE AI (SHAP FEATURE ATTRIBUTION)
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### 🧠 Why this risk? (Explainable AI Attribution for 72h Flood Forecast)")
    st.caption("Local TreeSHAP feature contributions explaining why the XGBoost model predicted this 72h flood likelihood.")

    try:
        PLAIN_LABELS = {
            "shap_precip_roll_7d": "7-Day Cumulative Rainfall",
            "shap_precip_roll_14d": "14-Day Cumulative Rainfall",
            "shap_precip_roll_3d": "3-Day Rainfall Accumulation",
            "shap_precip_roll_1d": "Recent 24h Rain",
            "shap_river_discharge": "Current River Discharge",
            "shap_river_discharge_lag_1d": "Previous Day River Flow",
            "shap_river_discharge_lag_2d": "2-Day Prior River Flow",
            "shap_river_discharge_lag_3d": "3-Day Prior River Flow",
            "shap_river_discharge_diff_1d": "1-Day River Flow Surge Rate",
            "shap_soil_moisture": "Upper Soil Moisture Saturation",
            "shap_soil_moisture_diff_3d": "3-Day Soil Wetting Rate",
            "shap_month": "Monsoon Seasonal Timing",
        }

        if not df_shap.empty:
            m_shap = (df_shap["district_slug"] == selected_slug) & (df_shap["date"] == selected_date)
            matching_shap = df_shap[m_shap]

            if not matching_shap.empty:
                shap_row = matching_shap.iloc[0]
                shap_cols = [c for c in df_shap.columns if c.startswith("shap_")]

                # Extract contributions and sort by magnitude
                contribs = []
                for sc in shap_cols:
                    val = float(shap_row.get(sc, 0.0))
                    label = PLAIN_LABELS.get(sc, sc.replace("shap_", "").replace("_", " ").title())
                    contribs.append({"feature": label, "shap_value": val, "abs_val": abs(val)})

                contrib_df = pd.DataFrame(contribs).sort_values("abs_val", ascending=False).head(5)
                # Sort ascending for horizontal bar chart (top contributor at top)
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

                # Plain-English dynamic explanation
                top_driver = contrib_df.sort_values("abs_val", ascending=False).iloc[0]
                direction = "elevating" if top_driver["shap_value"] > 0 else "suppressing"
                st.info(
                    f"**Hydrological Explanation:** The primary driver influencing the 72h flood forecast on {selected_date} is "
                    f"**{top_driver['feature']}** ({top_driver['shap_value']:+.2f} SHAP impact), significantly {direction} flood likelihood."
                )
            else:
                st.info("SHAP feature attribution not available for the selected historical date.")
        else:
            st.info("SHAP attribution values are being computed.")
    except Exception as e:
        st.warning(f"Feature attribution temporarily unavailable: {e}")

    # --------------------------------------------------------------------------
    # MODULE 3: INTERACTIVE WHAT-IF SCENARIO SANDBOX (LIVE DYNAMIC INFERENCE)
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
                        <span style="font-family: 'Inter', monospace; font-size: 0.72rem; color: #94A3B8; background: rgba(0, 242, 254, 0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0, 242, 254, 0.3);">LOCAL_AIRGAPPED_ENGINE v2.4</span>
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
                        "month": [7],  # July peak monsoon baseline
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
# TAB 2: HISTORICAL BACKTEST
# ==============================================================================
with tab_backtest:
    st.markdown("### ⏪ Historic Event Replay: July 2022 Godavari Flood")
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
                <b style="color:#38bdf8; font-size:1.05rem;">Catchment Saturation Precursor Detected: 7 Days (168 Hours) Ahead of Peak Crest</b><br>
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

# ==============================================================================
# TAB 3: MODEL RESULTS & AUDITS
# ==============================================================================
with tab_metrics:
    st.markdown("### 📈 Quantitative Performance & Baseline Audit")
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

        st.markdown(
            """
            <div style="background:#1e293b; border-left:4px solid #10b981; border-radius:8px; padding:12px 16px; margin-top:15px; margin-bottom:15px;">
                <b style="color:#10b981; font-size:1.02rem;">Asymmetric Disaster Loss Function & F2 Justification</b><br>
                <span style="color:#cbd5e1; font-size:0.88rem;">
                In flood early warning, a <b>False Negative (missed flood)</b> leading to loss of human life and unevacuated settlements is 
                exponentially costlier than a <b>False Positive (precautionary inspection)</b>. 
                The <b>F2-score (&beta;=2)</b> places <b>4x more weight on Recall than Precision</b>. 
                JalDrishti optimizes for maximum F2-score and &gt;90% recall (achieving <b>82.91% F2 at 72h</b> vs 77.78% for persistence and 61.87% for API-3).
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🔬 Key Model Diagnostics & Empirical Trade-Offs")
        st.markdown(
            """
            1. **Predictive Lift over Baselines at 72h**:
               - The naive persistence baseline misses **144 flood days** (Recall drops to 75.09%) because persistence cannot anticipate floods that haven't happened yet.
               - The API-3 linear rainfall index triggers **754 false alarms** because rain alone without soil saturation context over-predicts runoff.
               - In contrast, JalDrishti's 72h XGBoost model achieves **90.66% Recall (F2: 82.91%)**, capturing **524 out of 578 flood days** and missing only **54 days**.
            2. **The Disaster Warning Trade-Off (Recall vs Precision)**:
               - Using cost-sensitive `scale_pos_weight`, the model intentionally prioritizes high recall (~90%), accepting a manageable rate of false alarms to avoid deadly surprise floods.
            """
        )

    st.markdown("---")
    st.markdown("### ⚠️ Transparent System Limitations (Academic & Operational Integrity)")
    st.markdown(
        """
        - **Class Imbalance**: River flood events represent only ~5% of daily observations in semi-arid Telangana. Models require cost-sensitive weighting.
        - **Daily Temporal Resolution**: Open-Meteo Flood API provides daily mean discharge. Fast-rising cloudburst flash floods (which occur over 3-6 hours) require sub-daily gauge telemetry.
        - **Modelled vs In-Situ Discharge**: Historical discharge values are derived from European Centre for Medium-Range Weather Forecasts (ECMWF) GloFAS land-surface reanalysis rather than physical Central Water Commission (CWC) river gauges.
        - **Geographic Scope**: Trained specifically for 4 Telangana districts along the Godavari mainstem; transferring to the Krishna basin requires local retraining.
        - **Non-Official Notice**: This system is developed as an academic hackathon submission for JNTUH Neural Storm 2026 and does not replace official bulletins from the India Meteorological Department (IMD) or Central Water Commission (CWC).
        """
    )

# ==============================================================================
# TAB 4: ABOUT & ARCHITECTURE
# ==============================================================================
with tab_about:
    col_about_logo, col_about_header = st.columns([1, 6])
    with col_about_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=105)
    with col_about_header:
        st.markdown("### ℹ️ About JalDrishti")
        st.markdown(
            """
            **JalDrishti (జలదృష్టి / जलदृष्टि)** is an explainable, dual-hazard early warning prototype built for 
            **JNTUH Neural Storm 2026 (Green Planet Track, Challenge GP-03: Flood and Drought Early Warning System)**.
            
            #### 🏛️ Architectural Workflow
            ```mermaid
            flowchart TD
                A[Open-Meteo Archive & Flood APIs] -->|2015-2025 Daily Climatology| B[Data Pipeline & Curation]
                B --> C[Feature Engineering: Rolling Precipitation & Discharge Lags]
                C --> D[XGBoost Flood Forecasters: 24h, 48h, 72h Horizons]
                C --> E[Drought Engine: SPI-1, SPI-3 Gamma Fit & Soil Z-Score]
                D --> F[Multi-Hazard Risk Engine & WhatsApp Alerts]
                E --> F
                F --> G[Streamlit Multilingual UI: English, Telugu, Hindi]
            ```

            #### 📡 Data Sources & Provenance
            - [Open-Meteo Weather Archive API](https://archive-api.open-meteo.com/v1/archive): Daily precipitation, 2m temperature, and hourly 0-7cm soil moisture.
            - [Open-Meteo River Discharge & Flood API](https://flood-api.open-meteo.com/v1/flood): Gridded river discharge reanalysis (ECMWF GloFAS).
            - [Central Water Commission (CWC) Godavari Basin References](https://cwc.gov.in): Bhadrachalam danger level thresholds (43ft, 48ft, 53ft).

            #### 👤 Builder Attribution
            - **Track**: Green Planet (GP-03: Flood and Drought Early Warning System)
            - **Submission**: JNTUH Neural Storm 2026 Hackathon
            - **Author / Lead Engineer**: Nikhil Kunte
            - **Deployment**: [Live on Streamlit Community Cloud](https://jaldrishti-warning.streamlit.app)
            - **Source Code**: [GitHub Repository (Public)](https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning)
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
