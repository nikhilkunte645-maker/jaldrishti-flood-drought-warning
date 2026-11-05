# 🎤 JalDrishti — Hackathon Presentation & Live Demo Kit

**Hackathon:** JNTUH Neural Storm 2026 — Green Planet Track (GP-03)  
**System:** JalDrishti (జలదృష్టి / जलदृष्टि)  
**Author / Lead Engineer:** Nikhil Kunte (Team Prahar)  
**Live URL:** [https://jaldrishti-warning.streamlit.app](https://jaldrishti-warning.streamlit.app)

---

## ⚡ 1. The 30-Second High-Impact Elevator Pitch

> *"Respected judges, in July 2022, the Godavari river crested at an unprecedented 71.3 feet at Bhadrachalam, submerging dozens of habitations because frontline officials had neither hyper-local lead time nor explainable alerts in their mother tongue.*
>
> *We built **JalDrishti**—an explainable, dual-hazard early warning platform for river basins. Powered by cost-sensitive XGBoost optimized for high-recall disaster warning, JalDrishti achieves **90.66% Recall and 0.8291 F2-score** on out-of-time test data with a measured **2.33 millisecond CPU latency**.*
>
> *It decouples rapid 72-hour flood forecasts from 90-day agricultural drought monitoring, explains every prediction transparently using exact **TreeSHAP physics**, runs completely **offline without external APIs**, and dispatches instant, tiered emergency alerts in **Telugu, Hindi, and English** directly to frontline collectors and gram panchayats."*

---

## ⏱️ 2. The 2-Minute Live Demo Script (Step-by-Step Clicks)

### Total Duration: 120 Seconds

| Time | Target UI Location | Visual Click Action | Speaker Script (Verbatim Voiceover) |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:20** | **Header & Sidebar** | Open app at [jaldrishti-warning.streamlit.app](https://jaldrishti-warning.streamlit.app). Point to the official Brand Logo and the `[🟢 LIVE TELEMETRY]` badge. | *"Welcome to JalDrishti. Here on the sidebar, our system continuously monitors the Godavari basin using real-time Open-Meteo telemetry with automatic offline cache fallback. Notice the clean Dark Glassmorphism command center."* |
| **0:20 - 0:45** | **Tab 1: Rapid Flood Inundation** | Click on **Tab 1**. Point to the Folium basin map, the 24h/48h/72h risk horizon cards, and the 30-day hydrograph. | *"In Tab 1, we focus on rapid flood inundation. For Bhadradri Kothagudem on July 14, 2022, the 72h flood probability is 92.4% (High Risk). Below the hydrograph, our TreeSHAP explainability engine reveals exactly why: 7-day cumulative rainfall and upstream discharge are the dominant physical drivers."* |
| **0:45 - 1:05** | **Tab 1: Vernacular Alert & What-If Simulator** | Scroll to the WhatsApp container. Switch language to **తెలుగు (Telugu)**. Then scroll to the Scenario Sandbox, move the 24h rainfall slider to 120mm, and click **⚡ Run Live Hydraulic Inference**. | *"Disaster warnings fail if frontline villagers cannot understand them. JalDrishti synthesizes WhatsApp emergency broadcasts in Telugu and Hindi with tiered civil defense action stages. Below, our What-If sandbox lets engineers simulate hypothetical extreme rainfall pulses with sub-3ms CPU execution."* |
| **1:05 - 1:25** | **Tab 2: Drought Monitoring** | Switch to **Tab 2 (`Meteorological & Agricultural Drought`)**. Point to the SPI-1, SPI-3, and Soil Moisture Z-Score cards. | *"Unlike rapid floods, drought operates over seasonal timescales. In Tab 2, we decouple these dynamics using Standardized Precipitation Indices—SPI-1 for monthly weather and SPI-3 for 90-day root-zone crop stress—delivering specific agronomic contingency plans to Rythu Bharosa Kendras."* |
| **1:25 - 1:45** | **Tab 3: Model Audit & Backtest** | Switch to **Tab 3 (`Model Audit & Limitations`)**. Point to the July 2022 Backtest Replay and the Benchmark Table. | *"In Tab 3, we verify our models against the historic July 2022 flood, where sustained catchment saturation fired warnings 7 days prior to peak crest. On out-of-time test data (2022–2025), XGBoost achieves 90.66% recall under asymmetric F2 disaster loss, capturing 524 of 578 flood days where persistence baseline missed 144 days."* |
| **1:45 - 2:00** | **Tab 4: Operations & PDF Report** | Switch to **Tab 4 (`Operations & B2G Roadmap`)**. Point to the Mermaid Architecture diagram and the PDF download button. | *"JalDrishti is designed for public sector B2G adoption by State Disaster Management Authorities at ~₹1.5 Lakhs per district/year. The entire pipeline, audit reports, and documentation are available in one click. Thank you!"* |

---

## 🛡️ 3. Honest Limitations & Risk Register (Academic Integrity)

Every production engineering platform has physical boundaries. Being transparent about them demonstrates senior engineering maturity:

| Risk / Physical Limitation | Hydrological Impact | JalDrishti Mitigation / Engineering Countermeasure |
| :--- | :--- | :--- |
| **1. Confluence Backwater Effects** | At Bhadrachalam, downstream backwater from the Sabari River confluence (near Kunavaram) can artificially elevate flood gauge heights independently of upstream Godavari rain. | Explicitly highlighted in Tab 3 limitations; future iterations incorporate downstream hydraulic stage backwater equations. |
| **2. Flash Cloudbursts vs. Daily Temporal Step** | Open-Meteo flood reanalysis provides daily mean discharge. Intense 3-hour cloudbursts can cause local flash urban flooding before daily mean spikes. | System is framed for **regional riverine inundation** (72h forward horizon). Sub-daily flash flooding is recommended for high-frequency municipal gauge telemetry. |
| **3. Upstream Dam Gate Maneuvers** | Unannounced midnight gate releases from major upstream barrages (e.g., Sriram Sagar or Kadam Dam) can create abrupt surge waves not predicted by rainfall alone. | The feature pipeline tracks `river_discharge_diff_1d` (1-day rate of surge) to rapidly escalate risk when abrupt hydraulic jumps occur. |
| **4. Ungauged Tributaries in Eastern Ghats** | Dense tribal forest catchments in Mulugu and Bhadradri have limited physical rain gauges, relying on gridded satellite-reanalysis interpolation. | Soil moisture saturation anomalies (0–7 cm depth) are incorporated to account for unobserved rainfall that has already soaked into the forest soil mantle. |
| **5. Native Speaker Localization Review** | Automated algorithmic translations into Telugu and Hindi may contain dialect nuances that differ between Adilabad and Khammam. | Every alert payload explicitly includes the disclaimer tag: `[⚠️ Automated Draft Translation: Pending District Public Relations Officer (PRO) Native Review]`. |

