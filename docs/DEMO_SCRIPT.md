# 🎬 JalDrishti: 2-3 Minute Hackathon Demo Video Script
**Hackathon:** JNTUH Neural Storm 2026  
**Track:** Green Planet (GP-03: Flood and Drought Early Warning System)  
**System:** JalDrishti (జలదృష్టి / जलदृष्टि)  
**Target Region:** Godavari Basin, Telangana (Bhadradri Kothagudem, Mulugu, Nizamabad, Adilabad)  
**Author / Presenter:** Nikhil Kunte  

---

## ⏱️ Video Timeline & Screen Flow (Total Duration: 2 min 50 sec)

### [00:00 - 00:25] Introduction & The Crisis
- **Screen:** Open on the **JalDrishti Dashboard** (`https://jaldrishti-warning.streamlit.app`) with dark theme. Camera cursor points to the title and the tagline: *"Explainable flood and drought early warning in your own language"*.
- **Voiceover:**
  > *"Every monsoon, communities along the Godavari river basin in Telangana face devastating floods, followed by severe dry-season water stress. In July 2022, river levels at Bhadrachalam crossed the catastrophic 71-foot mark, displacing over 25,000 residents across Bhadradri Kothagudem. 
  > Hello evaluators, I am Nikhil Kunte presenting **JalDrishti**, an explainable, dual-hazard early warning system engineered specifically for the Telangana Godavari basin."*

---

### [00:25 - 01:05] Architecture & Live Dashboard Walkthrough
- **Screen:** Hover over the **Interactive Folium Map** of Telangana showing the 4 monitored districts (Adilabad, Nizamabad, Mulugu, Bhadradri Kothagudem). Click on Bhadradri Kothagudem.
- **Action:** Switch the vernacular language dropdown in the sidebar from **English** to **తెలుగు (Telugu)** and then **हिन्दी (Hindi)**. Show the **WhatsApp-style broadcast bubble** updating instantly into certified NDMA/TGSDMA emergency phraseology.
- **Voiceover:**
  > *"JalDrishti ingests 10 years of daily climatological reanalysis and hydrological discharge from Open-Meteo. 
  > Notice the map: each circle marker reflects real-time multi-hazard risk. 
  > Crucially, complex hydrological data is useless if rural farmers and frontline panchayat officials cannot understand it. 
  > With one click, JalDrishti translates mathematical probabilities into localized, WhatsApp-ready vernacular alerts in English, Telugu, and Hindi — validated against official state disaster management emergency phraseology for immediate broadcast."*

---

### [01:05 - 01:35] 72-Hour Flood Forecasting & SHAP Explainability
- **Screen:** Scroll down to the **Early Warning Horizon Matrix** (24h, 48h, 72h flood cards) and the **Drought Severity Card** (SPI-1, SPI-3, Soil Moisture Z-Score).
- **Action:** Point cursor to the **"Why this risk?" SHAP Horizontal Bar Chart**. Highlight the top feature: `Upper Soil Moisture Saturation` and `7-Day Cumulative Rainfall`.
- **Voiceover:**
  > *"Look at our forecast cards: we predict flood probabilities at 24h, 48h, and 72h lead times using cost-sensitive XGBoost classifiers trained strictly without future leakage. 
  > But black-box AI is dangerous in disaster response. Underneath our forecast, JalDrishti provides transparent TreeSHAP explainability. 
  > The model explicitly explains why the risk is elevated: here, 7-day cumulative rainfall and saturated upper soil moisture are pushing flood log-odds up, giving disaster managers clear physical reasoning before ordering an evacuation."*

---

### [01:35 - 02:00] Interactive What-If Scenario Sandbox (Live Simulator)
- **Screen:** Scroll to the **"🧪 Interactive Scenario Sandbox / Real-Time What-If Simulator"** card under the Risk Dashboard.
- **Action:** Drag the sliders: Set Simulated 24h Rain to `180 mm`, River Discharge to `120 m³/s`, and Soil Moisture to `85%`. Select Horizon `72h` and click **"⚡ Run Live Hydraulic Inference"**.
- **Visual:** Instant update showing Simulated Probability: `92.4% (CRITICAL HIGH RISK)` with an automated evacuation advisory.
- **Voiceover:**
  > *"New in our production upgrade is the Interactive Scenario Sandbox. 
  > Emergency response teams can dynamically stress-test the hydraulic model: simulating cloudbursts or upstream dam release surges in real-time. 
  > Clicking 'Run Live Hydraulic Inference' executes instant, air-gapped inference against our loaded XGBoost model, producing actionable operational advisories in milliseconds."*

---

### [02:00 - 02:25] Real Historical Backtest: July 2022 Godavari Flood
- **Screen:** Click on the second tab: **"⏪ Backtest: July 2022 Flood"**.
- **Action:** Hover over the interactive Plotly chart showing the river discharge surge peaking on **July 14, 2022 at 194.0 m³/s**, and the green vertical alert line triggered on **July 7, 2022**.
- **Voiceover:**
  > *"We never fake results. In our historical backtest tab, we replayed the real July 2022 Bhadrachalam disaster. 
  > While our ML target predicts a 72-hour forward window, persistent multi-day rains and catchment saturation triggered continuous High-Risk alerts starting July 7th. 
  > This provided a full **7-calendar-day (168-hour) catchment precursor warning** before the peak crest on July 14th, providing crucial time for reservoir pre-depletion and village evacuations."*

---

### [02:25 - 02:50] Asymmetric Loss Justification (F2-Score) & Conclusion
- **Screen:** Click on the **"📈 Model Results & Audits"** tab showing the metrics table comparing XGBoost against Persistence and the API-3 linear benchmark.
- **Voiceover:**
  > *"In disaster management, a False Negative (missed flood) is catastrophic. 
  > Therefore, we optimize mathematically for the **F2-Score**, weighting Recall 4 times more than Precision. 
  > At 72 hours, JalDrishti achieves an **82.91% F2-Score and 90.66% Recall**, capturing 524 of 578 flood days and crushing both persistence and the API-3 benchmark. 
  > Built solo with pure Python and live right now at jaldrishti-warning.streamlit.app. Thank you!"*
