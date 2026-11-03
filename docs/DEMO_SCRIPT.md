# 🎬 JalDrishti: 2-3 Minute Hackathon Demo Video Script
**Hackathon:** JNTUH Neural Storm 2026  
**Track:** Green Planet (GP-03: Flood and Drought Early Warning System)  
**System:** JalDrishti (జలదృష్టి / जलदृष्टि)  
**Target Region:** Godavari Basin, Telangana (Bhadradri Kothagudem, Mulugu, Nizamabad, Adilabad)  

---

## ⏱️ Video Timeline & Screen Flow (Total Duration: 2 min 45 sec)

### [00:00 - 00:30] Introduction & The Crisis
- **Screen:** Open on the **JalDrishti Dashboard** (`http://localhost:8501`) with dark theme. Camera cursor points to the title and the tagline: *"Explainable flood and drought early warning in your own language"*.
- **Voiceover:**
  > *"Every monsoon, communities along the Godavari river basin in Telangana face devastating floods, followed by severe dry-season water stress. In July 2022, river levels at Bhadrachalam crossed the catastrophic 71-foot mark, displacing over 25,000 residents across Bhadradri Kothagudem. 
  > Hello evaluators, I am a solo student developer presenting **JalDrishti**, an explainable, dual-hazard early warning system engineered specifically for the Telangana Godavari basin."*

---

### [00:30 - 01:15] Architecture & Live Dashboard Walkthrough
- **Screen:** Hover over the **Interactive Folium Map** of Telangana showing the 4 monitored districts (Adilabad, Nizamabad, Mulugu, Bhadradri Kothagudem). Click on Bhadradri Kothagudem.
- **Action:** Switch the vernacular language dropdown in the sidebar from **English** to **తెలుగు (Telugu)** and then **हिन्दी (Hindi)**. Show the **WhatsApp-style broadcast bubble** updating instantly into idiomatic Telugu.
- **Voiceover:**
  > *"JalDrishti ingests 10 years of daily climatological reanalysis and hydrological discharge from Open-Meteo. 
  > Notice the map: each circle marker reflects real-time multi-hazard risk. 
  > Crucially, complex hydrological data is useless if rural farmers and frontline panchayat officials cannot understand it. 
  > With one click, JalDrishti translates mathematical probabilities into localized, WhatsApp-ready vernacular alerts in English, Telugu, and Hindi — ready for instant broadcast to panchayat WhatsApp groups."*

---

### [01:15 - 01:50] 72-Hour Flood Forecasting & SHAP Explainability
- **Screen:** Scroll down to the **Early Warning Horizon Matrix** (24h, 48h, 72h flood cards) and the **Drought Severity Card** (SPI-1, SPI-3, Soil Moisture Z-Score).
- **Action:** Point cursor to the **"Why this risk?" SHAP Horizontal Bar Chart**. Highlight the top feature: `7-Day Cumulative Rainfall (+1.42)` and `Upper Soil Moisture Saturation (+1.18)`.
- **Voiceover:**
  > *"Look at our forecast cards: we predict flood probabilities at 24h, 48h, and 72h lead times using cost-sensitive XGBoost classifiers trained strictly without future leakage. 
  > But black-box AI is dangerous in disaster response. Underneath our forecast, JalDrishti provides transparent TreeSHAP explainability. 
  > The model explicitly explains why the risk is elevated: here, 7-day cumulative rainfall and saturated upper soil moisture are pushing flood log-odds up, giving disaster managers clear physical reasoning before ordering an evacuation."*

---

### [01:50 - 02:25] Real Historical Backtest: Replaying the July 2022 Flood
- **Screen:** Click on the second tab: **"⏪ Backtest: July 2022 Flood"**.
- **Action:** Hover over the interactive Plotly chart showing the river discharge surge peaking on **July 14, 2022 at 194.0 m³/s**, and the green vertical alert line triggered on **July 7, 2022**.
- **Voiceover:**
  > *"We never fake results. In our historical backtest tab, we replayed the real July 2022 Bhadrachalam disaster. 
  > The observed river discharge peaked at 194.0 m³/s on July 14th — far exceeding the 95th percentile flood threshold of 80.9 m³/s. 
  > JalDrishti's 72-hour model crossed the HIGH RISK threshold on **July 7th**, a full **7 days (168 hours)** before the peak, providing actionable lead time for emergency evacuation and reservoir pre-depletion."*

---

### [02:25 - 02:45] Quantitative Proof, Limitations & Conclusion
- **Screen:** Click on the **"📈 Model Results & Audits"** tab showing the metrics table comparing XGBoost against the Naive Persistence baseline.
- **Voiceover:**
  > *"Compared to a persistence baseline which missed 144 flood days, JalDrishti achieves **90.66% recall** at 72 hours, missing only 54 flood events out of 578. 
  > Built with pure Python, scikit-learn, XGBoost, and Streamlit, running completely air-gapped without runtime external API dependencies. 
  > JalDrishti bridges machine learning and grassroots disaster resilience for a safer planet. Thank you!"*
