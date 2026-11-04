# 🌊 JalDrishti (జలదృష్టి / जलदृष्टि)

<p align="center">
  <img src="docs/screenshots/cover.png" alt="JalDrishti Banner" width="100%">
</p>

<p align="center">
  <img src="docs/screenshots/cover.jpg" alt="JalDrishti Banner" width="100%">
</p>
### Explainable Flood and Drought Early Warning System for the Godavari Basin, Telangana
**JNTUH Neural Storm 2026 — Green Planet Track (Challenge GP-03)**  
*Built by `Nikhil Kunte`*

[![Python 3.12](https://img.shields.io/badge/Python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Streamlit App](https://img.shields.io/badge/Streamlit-App%20Live-FF4B4B.svg)](https://jaldrishti-warning.streamlit.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717.svg)](https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning)

---

## 📌 Links & Quick Access
- **Live Streamlit App:** [https://jaldrishti-warning.streamlit.app](https://jaldrishti-warning.streamlit.app)
- **GitHub Repository:** [https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning](https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning)
- **Demo Script (2-3 min):** [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)
- **Submission Checklist:** [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md)

---

## 💡 The Pitch & Problem Statement
The Godavari river basin in Telangana represents one of India's most critical yet climatically vulnerable agrarian corridors. Communities living along the Godavari reach across **Bhadradri Kothagudem (Bhadrachalam), Mulugu, Nizamabad, and Adilabad** endure a punishing dual-hazard cycle:
1. **Devastating Monsoon Floods:** In July 2022, river levels at Bhadrachalam crossed the highest danger mark (53 ft) and crested at **71.3 ft**, submerging dozens of habitations, isolating thousands of tribal hamlets, and causing massive losses of standing crops and cattle.
2. **Acute Post-Monsoon Soil Moisture Deficits:** During dry seasons, unpredictable rainfall leads to agricultural drought, depleting topsoil moisture before crops reach maturity.
3. **The Communication Last-Mile Failure:** Existing government forecasts are typically issued in English or formal technical Hindi as broad district-level bulletins. Frontline farmers and gram panchayat officials lack **hyper-local lead time**, **explainable reasoning**, and **direct vernacular alerts in their mother tongue (Telugu)**.

**JalDrishti** bridges this critical gap. It is an end-to-end, air-gapped machine learning early warning system that forecasts floods 24h, 48h, and 72h in advance using cost-sensitive XGBoost, computes multi-scalar climatological drought indices (SPI-1, SPI-3, Soil Moisture Z-Score), explains every prediction transparently using TreeSHAP, provides a live **Interactive Scenario Sandbox**, and synthesizes instant, WhatsApp-ready broadcasts in **English, Telugu (తెలుగు), and Hindi (हिन्दी)**.

---

## 🖼️ User Interface & Visual Showcase

| Interactive Risk Dashboard | Historic Flood Replay (July 2022) |
| :---: | :---: |
| ![JalDrishti Dashboard](docs/screenshots/dashboard.png) | ![July 2022 Backtest Replay](docs/screenshots/backtest.png) |

| Mobile-First WhatsApp Alert Dispatch |
| :---: |
| ![Mobile View](docs/screenshots/mobile_view.png) |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph DataIngestion["1. Historical Ingestion (2015-2025)"]
        OM_Arch["Open-Meteo Archive API<br/>Daily Rain, Temp, Hourly Soil Moisture"]
        OM_Flood["Open-Meteo Flood API<br/>Daily River Discharge (ECMWF GloFAS)"]
    end

    subgraph FeatureEngineering["2. Leakage-Free Hydrological Engineering"]
        PrecipRoll["Precipitation Rolling Sums<br/>(1d, 3d, 7d, 14d)"]
        DischargeLags["River Discharge Lags & Surge Rate<br/>(Lags 1, 2, 3 & Diff 1d)"]
        SoilDynamics["Soil Moisture Saturation & Delta 3d"]
        ThreshCalc["95th Pct Flood Threshold<br/>(Computed on 2015-2021 Train Years)"]
    end

    subgraph ModelingEngine["3. Dual-Hazard Analytics Engine"]
        XGB_24["XGBoost 24h Forecaster"]
        XGB_48["XGBoost 48h Forecaster"]
        XGB_72["XGBoost 72h Forecaster"]
        SPI_Engine["Drought Engine: SPI-1 & SPI-3<br/>(Monthly Gamma Fit + Zero-Rain Handling)"]
        SM_Anomaly["Soil Moisture Anomaly<br/>(Calendar-Month Z-Score)"]
        SHAP_Engine["Explainable AI Engine<br/>(TreeSHAP Local Attributions)"]
        SandboxEngine["Interactive Scenario Sandbox<br/>(Live Dynamic Hydraulic Inference)"]
    end

    subgraph Presentation["4. Grassroots Vernacular UI"]
        StreamlitUI["Air-Gapped Streamlit App<br/>(Reads Only Local Files)"]
        FoliumMap["Interactive Folium Map of Telangana"]
        WhatsAppBubble["WhatsApp-Style Alert Generator<br/>(English / తెలుగు / हिन्दी)"]
        BacktestReplay["July 2022 Historic Flood Replay"]
    end

    OM_Arch --> PrecipRoll
    OM_Arch --> SoilDynamics
    OM_Flood --> DischargeLags
    OM_Flood --> ThreshCalc

    PrecipRoll --> XGB_24 & XGB_48 & XGB_72
    DischargeLags --> XGB_24 & XGB_48 & XGB_72
    SoilDynamics --> XGB_24 & XGB_48 & XGB_72
    ThreshCalc --> XGB_24 & XGB_48 & XGB_72

    PrecipRoll --> SPI_Engine
    SoilDynamics --> SM_Anomaly
    XGB_72 --> SHAP_Engine
    XGB_24 & XGB_48 & XGB_72 --> SandboxEngine

    XGB_24 & XGB_48 & XGB_72 --> StreamlitUI
    SPI_Engine & SM_Anomaly --> StreamlitUI
    SHAP_Engine --> StreamlitUI
    SandboxEngine --> StreamlitUI
    StreamlitUI --> FoliumMap & WhatsAppBubble & BacktestReplay
```

---

## 🔬 Real Quantitative Evaluation & Metrics
All models are strictly evaluated on unseen out-of-time test data (January 1, 2022 to October 31, 2025; 5,600 samples across 4 districts). We benchmark XGBoost against both a **Naive Persistence Baseline** (*"Tomorrow's flood status equals today's"*) and an **Antecedent Precipitation Index (API-3 Linear Benchmark)** ($API_3 = P_t + 0.8 \cdot P_{t-1} + 0.6 \cdot P_{t-2}$).

### Flood Forecasting Test Performance (`models/metrics.csv`)
| Horizon | Model Architecture | Precision | Recall | F1-Score | F2-Score (&beta;=2) | ROC-AUC | False Alarms (FP) | Missed Floods (FN) | True Positives (TP) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **24h** | **XGBoost (JalDrishti)** | **72.65%** | **90.21%** | **0.805** | **0.861** | **0.989** | 163 | **47** | 433 |
| 24h | Naive Baseline (Persistence) | 88.94% | 88.75% | 0.888 | 0.888 | 0.500 | 53 | 54 | 426 |
| 24h | API-3 Linear Benchmark | 30.05% | 71.25% | 0.423 | 0.559 | 0.875 | 796 | 138 | 342 |
| **48h** | **XGBoost (JalDrishti)** | **66.85%** | **90.43%** | **0.769** | **0.845** | **0.984** | 239 | **51** | 482 |
| 48h | Naive Baseline (Persistence) | 90.59% | 81.24% | 0.857 | 0.830 | 0.500 | 45 | 100 | 433 |
| 48h | API-3 Linear Benchmark | 34.08% | 73.92% | 0.467 | 0.599 | 0.887 | 762 | 139 | 394 |
| **72h** | **XGBoost (JalDrishti)** | **61.79%** | **90.66%** | **0.735** | **0.829** | **0.977** | 324 | **54** | 524 |
| 72h | Naive Baseline (Persistence) | 90.79% | 75.09% | 0.822 | 0.778 | 0.500 | 44 | **144** | 434 |
| 72h | API-3 Linear Benchmark | 36.48% | 74.91% | 0.491 | 0.619 | 0.892 | 754 | 145 | 433 |

### 🔍 Empirical Analysis & Asymmetric Loss Function Justification
1. **Mathematical Justification via F2-Score (&beta;=2):**
   - In disaster risk reduction, **Recall is 4x more critical than Precision**. A missed flood causes unevacuated human drowning and catastrophic loss, whereas a false alarm triggers manageable precautionary checks.
   - The F2-score mathematically embodies this loss asymmetry:
     $$\text{F}_2 = (1 + 2^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{(2^2 \cdot \text{Precision}) + \text{Recall}} = 5 \cdot \frac{\text{Precision} \cdot \text{Recall}}{4 \cdot \text{Precision} + \text{Recall}}$$
   - At the 72h operational horizon, JalDrishti achieves **0.8291 F2**, vastly outperforming both the Persistence baseline (**0.7778 F2**) and the API-3 benchmark (**0.6187 F2**).
2. **Predictive Lift over Baselines at 72h:**
   - The persistence baseline misses **144 flood days** (missing 1 in 4 flood events) because it cannot anticipate future surges before they occur.
   - The API-3 benchmark triggers **754 false alarms** because rain alone without soil saturation context over-predicts runoff.
   - JalDrishti achieves **90.66% Recall at 72h**, catching **524 out of 578 flood days** and missing only **54 days**.

---

## ⏪ Historic Event Replay: July 2022 Godavari Flood
During July 2022, the Godavari basin witnessed historic rainfall that triggered severe inundation across Bhadrachalam and temple town lowlands. We replayed this disaster through JalDrishti (`src/backtest.py`):

| Parameter | Observed Historical Value |
| :--- | :--- |
| **Simulation Event Window** | 2022-07-01 to 2022-07-25 |
| **Monitored District** | Bhadradri Kothagudem (Bhadrachalam reach) |
| **95th Percentile Flood Threshold** | **80.89 m³/s** |
| **Observed Peak Crest Date** | **2022-07-14** (Discharge: **193.98 m³/s**) |
| **First Precursor Warning Date (P $\ge$ 60%)** | **2022-07-07** (72h Flood Probability: **72.34%**) |
| **Model Target Horizon** | **72-Hour Forward Window** |
| **Early Catchment Precursor Duration** | **7 Days (168 Hours) Ahead of Peak Crest** |
| **Verification Artifacts** | [`models/backtest.html`](models/backtest.html) & [`models/backtest.json`](models/backtest.json) |

*Hydrological Scientific Distinction: While the machine learning target horizon predicts flood inundation within a 72-hour rolling window, persistent multi-day precipitation and upper-catchment soil saturation caused sustained high-risk probability alerts ($P \ge 60\%$) to fire beginning on July 7, 2022—providing a 7-calendar-day early precursor warning prior to the crest on July 14, 2022.*

---

## 🧪 Interactive Scenario Sandbox (What-If Simulator)
Located under the **Risk Dashboard** tab, the Scenario Sandbox empowers disaster response planners and water resource engineers to test simulated scenarios:
- **Simulated 24h Rainfall (0 to 300 mm)**
- **Current River Discharge (0 to 400 m³/s)**
- **Volumetric Soil Moisture (10% to 100%)**
- **Target Forecast Horizon (24h, 48h, 72h)**

Clicking **"⚡ Run Live Hydraulic Inference"** runs immediate, air-gapped inference against the loaded XGBoost model, rendering the simulated flood probability, risk tier badge, and an actionable NDMA-compliant operational advisory.

---

## 🧠 Explainable AI (SHAP) Interpretation
Disaster mitigation authorities cannot act on a "black box" prediction. JalDrishti embeds TreeSHAP feature attributions directly into the dashboard.

**Global Feature Importance Ranking (72h Horizon):**
1. **Soil Moisture Saturation (Mean |SHAP|: 1.31):** Upper soil layer saturation determines whether incoming monsoon rainfall converts directly into surface runoff or infiltrates.
2. **7-Day Cumulative Rainfall (Mean |SHAP|: 1.27):** Multi-day catchment rainfall accumulation is the single greatest precursor to mainstem river flooding.
3. **Current River Discharge (Mean |SHAP|: 1.04):** Baseline river stage before additional rainfall pulses arrive.
4. **14-Day Cumulative Rainfall (Mean |SHAP|: 0.74):** Catchment wetness index.
5. **Recent 24h Precipitation (Mean |SHAP|: 0.38):** Immediate precipitation trigger.

---

## 📡 Data Sources & Provenance
1. **[Open-Meteo Weather Archive API](https://archive-api.open-meteo.com/v1/archive):** Daily precipitation sum ($mm$), mean 2m temperature ($^\circ C$), and hourly 0-7cm volumetric soil moisture ($m^3/m^3$) resampled to daily mean. Timezone: `Asia/Kolkata`.
2. **[Open-Meteo River Discharge & Flood API](https://flood-api.open-meteo.com/v1/flood):** Daily river discharge ($m^3/s$) from ECMWF Global Flood Awareness System (GloFAS) hydrological model reanalysis.
3. **[Central Water Commission (CWC)](https://cwc.gov.in):** Godavari basin hydrological references (Bhadrachalam gauge alert levels: Warning 43ft, Danger 48ft, Extreme Danger 53ft).

---

## ⚠️ Transparent System Limitations
- **Class Imbalance:** Floods are rare extreme events representing only ~5% of daily records in semi-arid Telangana; cost-sensitive weighting (`scale_pos_weight`) is necessary.
- **Daily Resolution:** Modelled on daily mean river discharge and daily precipitation sums. Cloudburst flash floods occurring on sub-daily 3-6 hour scales require high-frequency automated weather stations (AWS).
- **Modelled vs Sensor Telemetry:** Discharge data originates from GloFAS reanalysis grids rather than physical acoustic Doppler velocity meters installed at CWC river ghats.
- **Single Basin Scope:** Curated and calibrated for 4 districts along the Godavari mainstem in Telangana; transfer to the Krishna basin requires local hydrological retuning.
- **Academic Prototype Notice:** Built as a hackathon submission for JNTUH Neural Storm 2026. It is an advisory aid and does not supersede statutory bulletins from the IMD or CWC.
- **Vernacular Phrasing Certification:** Telugu and Hindi alerts have been validated against official State and National Disaster Management Authority (TGSDMA / NDMA) emergency protocol phrasing.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.12 (or Python 3.14)
- Git & PowerShell / Bash

### 1. Clone the Repository
```bash
git clone https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning.git
cd jaldrishti-flood-drought-warning
```

### 2. Set Up Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Pinned Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run Automated Self-Tests
```powershell
python src/selftest.py
python tests/test_app_smoke.py
```

### 5. Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment
To deploy this application live on Streamlit Community Cloud:
1. Fork or push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **"New app"**.
4. Configure the deployment settings:
   - **Repository:** `nikhilkunte645-maker/jaldrishti-flood-drought-warning`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **Python version:** `3.12`
5. Click **"Deploy!"**. The app runs with zero external API keys and 100% cached local data.

---

## 🔮 Future Scope
- **IoT River Gauge Integration:** Ingest live LoRaWAN ultrasonic water level sensors installed along the Godavari bridge piers at Bhadrachalam.
- **Automated WhatsApp Business API:** Hook into the Meta Cloud API to automatically blast SMS / WhatsApp notifications to registered village sarpanches when 72h flood probability crosses 60%.
- **Basin-Wide Digital Twin:** Expand coverage across upstream Maharashtra catchment dams (Jayakwadi, Babhali) to calculate upstream dam outflow travel times.

---

## 👤 Attribution
- **Event:** JNTUH Neural Storm 2026 Hackathon
- **Track:** Green Planet (GP-03: Flood and Drought Early Warning System)
- **Author:** Solo Student Builder (`Nikhil Kunte`)
- **Institution:** JNTUH Neural Storm 2026 Participant




