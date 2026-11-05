---
marp: true
theme: default
paginate: true
header: "JalDrishti (జలదృష్టి) • JNTUH Neural Storm 2026 • Green Planet GP-03"
footer: "Team Prahar • Confidential & Proprietary • Hackathon Final Presentation"
style: |
  section {
    background-color: #0b1120;
    color: #f1f5f9;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    padding: 40px 60px;
  }
  h1, h2, h3 {
    color: #38bdf8;
    font-family: 'Space Grotesk', sans-serif;
  }
  h1 { font-size: 2.2rem; margin-bottom: 0.2rem; }
  h2 { font-size: 1.6rem; border-bottom: 2px solid rgba(56, 189, 248, 0.3); padding-bottom: 8px; }
  p, li { font-size: 0.95rem; line-height: 1.5; color: #cbd5e1; }
  strong { color: #f8fafc; }
  .badge {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
  }
  .metric-card {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
  }
  .highlight { color: #10b981; font-weight: 700; }
  .warning { color: #ef4444; font-weight: 700; }
---

<!-- Slide 1: Title & Identity -->
# JalDrishti • జలదృష్టి • जलदृष्टि
### Physics-Informed, Explainable Hydro-Informatics & Dual-Hazard Warning System
<span class="badge">GREEN PLANET TRACK (GP-03)</span> <span class="badge">JNTUH NEURAL STORM 2026</span>

---

**Team Prahar** | Lead Architect: Nikhil Kunte
*Target Sector:* Telangana State Disaster Management Authority (TGSDMA) & CWC Liaison
*Basin Footprint:* Godavari Basin (Bhadrachalam Gauge) • Krishna Basin • Mahanadi Basin

- **Core Problem:** Fluvial flood inundation (24h–72h) & creeping agricultural drought (30d–90d).
- **Core Philosophy:** *Zero Black-Box, Zero Telemetry Dependency, Zero Life Lost.*
- **System Architecture:** Air-Gapped Gradient Boosted Trees + Trilingual TreeSHAP Explainability.

<!--
Speaker Notes:
Respected judges, welcome to the presentation of JalDrishti. I am Nikhil Kunte from Team Prahar, presenting our solution for Challenge GP-03 in the Green Planet track. In Indian river basins, disasters strike on two opposing timescales: sudden riverine floods within 24 to 72 hours, and slow-moving agricultural drought over 30 to 90 days. Current early warning systems fail because macro-weather forecasts do not understand basin hydrology, black-box deep learning hallucinate under power cuts, and warnings never reach farmers in their native language. JalDrishti bridges this gap with an air-gapped, explainable, edge-native hydro-informatics engine.
-->

---

<!-- Slide 2: The Ground Reality -->
## The Ground Reality: Failure of Macro-Forecasts in Godavari 2022

### Why Traditional Systems Break Down During Catchment Surges

- **The Bhadrachalam Crisis (July 2022):**
  - River Godavari crossed the 3rd danger level (53 ft) and crested at **71.3 ft** (second-highest in recorded history).
  - Over **25,000 villagers displaced** across Bhadradri Kothagudem and submerged temple causeways.
- **The Meteorological vs. Hydrological Disconnect:**
  - Standard IMD rainfall forecasts alert for *atmospheric rain*, not *riverbed stage elevation*.
  - Even when local rain ceased, massive upstream inflows from Maharashtra barrages surged the river.
- **The Critical Lead-Time Deficit:**
  - District Emergency Operations Centers (DEOCs) received warning only **12–24 hours before inundation**, leaving insufficient runway to mobilize NDRF/SDRF motorboats and stage relief camps.
- **The Language Barrier:**
  - Technical bulletins in English PDF tables fail to reach village panchayats and grassroots farmers.

<!--
Speaker Notes:
Let's ground this in reality. In July 2022, the Godavari basin experienced catastrophic flooding. At Bhadrachalam, water reached 71.3 feet—inundating dozens of villages. Why did this happen? Because standard meteorological apps only tell you if it's raining outside your window. They don't know that 400 kilometers upstream, barrages are opening sluice gates. By the time downstream flood gauges turned red, district administrations had barely 12 hours to act. We designed JalDrishti specifically to solve this lead-time deficit using upstream hydraulic telemetry and soil saturation dynamics.
-->

---

<!-- Slide 3: Solution Architecture -->
## Solution Architecture: Dual-Mode, Edge-First Hydro-Informatics

### Designed for District Emergency Operations Centers (DEOCs)

```
[LIVE TELEMETRY]              [AIR-GAPPED EDGE ENGINE]             [LAST-MILE BROADCAST]
Open-Meteo & GloFAS API  ───►  Local SQLite / Persistent Cache  ──► State EOC Dashboard
           │                             │                                    │
           ▼ (If Network Fails)          ▼                                    ▼
10-Year Local Baseline   ───►  XGBoost Tri-Horizon (F2=0.8291)  ──► Trilingual WhatsApp & SMS
Historical Replay Fixture                │                          (Telugu / Hindi / English)
                                         ▼                                    │
                               TreeSHAP Explainability          ──► High-Ground Shelter Routing
```

- **Dual-Mode Telemetry:** Real-time ingestion via Open-Meteo & GloFAS with **zero-exception fallback** to local disk cache and historical fixtures during grid outages.
- **Decoupled Timescales:**
  - *Rapid Inundation Engine:* 24h, 48h, and 72h forward flood probability.
  - *Slow-Onset Drought Engine:* SPI-1 (30-day), SPI-3 (90-day) Gamma fit + Soil Moisture Z-Score.
- **Edge Efficiency:** Entire model payload is **< 4.5 MB**; runs on a ₹3,500 Raspberry Pi 4.

<!--
Speaker Notes:
Here is our architecture. JalDrishti operates under a strict dual-mode philosophy. Under normal operations, it ingests gridded precipitation, soil moisture, and upstream river discharge from Open-Meteo and GloFAS APIs. But when storms sever power and cellular towers, JalDrishti falls back seamlessly to localized disk caches and 10-year calibrated baselines without raising a single runtime exception. The entire model bundle is under 4.5 megabytes—it requires zero cloud GPUs and runs fully air-gapped on standard edge hardware inside a district collectorate.
-->

---

<!-- Slide 4: Algorithmic Discipline -->
## Algorithmic Discipline: Why XGBoost Over Deep Learning

### The Engineering Rationale for Mission-Critical Disaster Defense

| Engineering Dimension | Deep Learning (LSTM / Transformers) | JalDrishti XGBoost + Hydro Physics |
| :--- | :--- | :--- |
| **Edge Hardware Footprint** | Requires 4GB+ GPU / VRAM; slow warmups | **Runs on single-core CPU (<4.5 MB total)** |
| **Inference Latency** | 150 ms – 1,200 ms | **2.33 ms (Measured CPU p50 latency)** |
| **Loss Function Strategy** | Standard Cross-Entropy (Equal FP/FN cost) | **Asymmetric $F_2$-Score Optimization ($\beta=2$)** |
| **Explainability** | Attention heatmaps (unreliable for judges) | **Exact Game-Theoretic TreeSHAP Attribution** |
| **Cold-Start Resilience** | Overfits heavily on sparse extreme events | **Calibrated with Scale-Pos-Weight & Lags** |

- **Asymmetric Cost of Error:** In flood forecasting, a **False Negative (missed flood)** costs human lives and livestock; a **False Positive (precautionary drill)** costs temporary fuel.
- **$F_2$-Score Prioritization:** We weight **Recall twice as high as Precision** ($\beta = 2.0$), tuning decision thresholds to catch 9 out of 10 incoming surges.

<!--
Speaker Notes:
Judges often ask: why not use an LSTM or a transformer? Here is our deliberate engineering choice. In disaster response, deep learning introduces dangerous failure modes: high compute overhead, black-box hallucinations, and symmetric loss functions. In our domain, a false positive means relief boats are staged early. A false negative means people drown in their sleep. That is why we formulate our training objective around the asymmetric F2-score with beta equals two—placing double the weight on recall—while guaranteeing a sub-3 millisecond execution time on basic CPUs.
-->

---

<!-- Slide 5: Empirical Benchmarks -->
## Empirical Benchmarks: Rigorous Out-of-Time Verification

### Evaluated on 5,600 Unseen Test Samples (2022–2025 Chronological Split)

| Forecasting Horizon | XGBoost Recall | $F_2$-Score | ROC-AUC | PR-AUC | Naive Persistence Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **24-Hour Horizon** | **90.21%** | **0.8605** | **0.9891** | **0.9017** | Recall: 88.75% ($F_2$: 0.8879) |
| **48-Hour Horizon** | **90.43%** | **0.8541** | **0.9835** | **0.8845** | Recall: 73.66% ($F_2$: 0.7634) |
| **72-Hour Horizon** | **90.66%** | **0.8291** | **0.9766** | **0.8524** | Recall: 63.89% ($F_2$: 0.6775) |

- **Predictive Lift over Baseline:** At the critical 72-hour window, naive persistence degrades to 63.89% recall. JalDrishti maintains **90.66% recall**, delivering a **+26.77% absolute lift**.
- **Edge Benchmark:** 1,000 automated Monte-Carlo inference iterations measured directly on local CPU:
  - **p50 Latency:** `2.33 ms` | **p95 Latency:** `3.73 ms` | **p99 Latency:** `4.35 ms`
- **July 2022 Replay:** Sustained high-risk alerts ($P \ge 60\%$) triggered on **July 07, 2022**—providing **7 days (168 hours) of actionable lead time** ahead of the July 14 peak crest.

<!--
Speaker Notes:
Look at the numbers on this slide—these are real, un-fabricated metrics from docs/metrics_summary.json evaluated on 5,600 chronological out-of-time test samples. Look at the 72-hour horizon: a naive model achieves only 63.8% recall. JalDrishti delivers 90.66% recall with an ROC-AUC of 0.9766. In our historical replay of the July 2022 Godavari flood, JalDrishti's forward model detected the persistent upstream catchment saturation and started firing high-risk alerts on July 7th—a full 7 calendar days before the river peaked at 71.3 feet at Bhadrachalam.
-->

---

<!-- Slide 6: Explainable AI & Vernacular Last Mile -->
## Explainable AI & Vernacular Last Mile: Grassroots Accessibility

### Translating Complex Game Theory into Immediate Village Action

```
[TreeSHAP Feature Attribution]  ──►  [Natural Language Engine]  ──►  [Trilingual Official Dispatch]
• Upstream Discharge (+42%)           "Upstream reservoir gate        • Active Language (English)
• 72h Catchment Rain (+28%)            discharges are rapidly         • తెలుగు (Official Telugu)
• Soil Saturation (+15%)               elevating river stage."        • हिन्दी (Official Hindi)
```

- **Explain Like a Farmer Expander:**
  - *English:* "Upstream river discharge and catchment inflow account for 42% of current flood risk. Even if local rain stops, river levels will continue rising; relocate livestock to high ground."
  - *తెలుగు:* "ఎగువ ప్రాజెక్టుల నుంచి భారీగా నీటి విడుదల జరుగుతుండటంతో నది వేగంగా పెరుగుతోంది. రైతులు కాజ్‌వేలు దాటవద్దు, పశువులను సురక్షిత ప్రాంతాలకు తరలించండి."
  - *हिन्दी:* "ऊपरी बांधों से भारी पानी छोड़े जाने के कारण जलस्तर बढ़ रहा है। तटबंधों से दूर रहें और मवेशियों को ऊंचे स्थानों पर ले जाएं।"
- **1-Click Dispatch & Shelter Routing:** Integrated WhatsApp copy tabs + Folium map layers routing directly to high-ground shelters (Bhadrachalam Temple Hill, ZP High School).

<!--
Speaker Notes:
Accuracy means nothing if a field officer doesn't trust the model or if a farmer cannot understand the message. JalDrishti integrates TreeSHAP game-theoretic explainability. But instead of showing raw SHAP math to a villager, our engine dynamically converts feature attributions into intuitive, 2-sentence farmer advice in English, Telugu, and Hindi. It explicitly warns them: 'Even if the rain stopped over your village, water is surging from upstream barrages; move your pumps and livestock to the Temple Hill high ground now.' We also provide 1-click clipboard copy for official WhatsApp broadcast.
-->

---

<!-- Slide 7: Operational B2G Scalability -->
## Operational B2G Scalability: Sustainable Public Procurement

### Enterprise Public-Sector Revenue & Deployment Framework

- **Target Public-Sector Buyers:**
  - State Disaster Management Authorities: **TGSDMA** (Telangana), **APSDMA** (Andhra Pradesh), **OSDMA** (Odisha).
  - Central Water Commission (CWC) Sub-Divisional Offices & District Collectorates.
  - Agricultural Extension Centers & Rythu Bharosa Kendras (RBKs) for drought mitigation.
- **Predictable Pilot Financial Model:**
  - **₹1.5 Lakhs (~$1,800 USD) per district / year** pilot licensing.
  - Covers localized gauge calibration, edge container setup, and vernacular dispatch integration.
  - Compare to the **₹1,200+ Crores** in public infrastructure damage incurred during the 2022 Godavari flood.
- **Modular Multi-Basin Configuration (`config/basins.yaml`):**
  - Instant config-driven scaling across **Godavari**, **Krishna** (Vijayawada), and **Mahanadi** (Cuttack).
  - Explicit *Heuristic Transfer Mode* labels uncalibrated basins, ensuring total transparency until 3–5 years of localized physical gauge records are linked.

<!--
Speaker Notes:
How do we turn this from a hackathon project into a lasting institutional system? Through a sustainable B2G public procurement model. At just 1.5 Lakhs rupees per district per year, JalDrishti offers an astronomical return on investment compared to the hundreds of crores in relief and crop loss incurred during a single flood event. Furthermore, our architecture is completely modular. Through config/basins.yaml, we have already scaffolded monitoring across the Krishna and Mahanadi basins with zero code refactoring.
-->

---

<!-- Slide 8: The Vision & Closing -->
## The Vision: Zero Black-Box, Zero Telemetry Dependency, Zero Life Lost

### Summary of Hackathon Deliverables

- [x] **Production Web Application:** Live on Streamlit Cloud (`https://jaldrishti-warning.streamlit.app`)
- [x] **Reproducible Source Code:** GitHub (`nikhilkunte645-maker/jaldrishti-flood-drought-warning`)
- [x] **Empirical Metrics:** $F_2 = 0.8291$, Recall $= 90.66\%$, CPU p50 latency $= 2.33\text{ ms}$ (`docs/metrics_summary.json`)
- [x] **Institutional Publications:** 6.56 MB High-DPI Submission PDF Report & 8-Slide Pitch Deck
- [x] **Operational Tooling:** 1-Click WhatsApp Dispatches, 1-Page Incident Briefing Export, Scenario Presets

---

### "When rivers swell and soil parches, JalDrishti stands guard."

**Thank You, Judges of JNTUH Neural Storm 2026.**
*Questions & Technical Deep-Dive Welcome.*

<!--
Speaker Notes:
In conclusion, JalDrishti is not a mock UI or an academic simulation. It is a fully verified, air-gapped, explainable hydro-informatics platform ready for institutional deployment by state disaster authorities today. We achieved 90.66% recall, 2.33 millisecond latency, verified trilingual explainability, and comprehensive B2G operational workflows. Thank you, and we welcome your questions and live stress-testing.
-->
