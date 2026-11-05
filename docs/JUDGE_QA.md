# 🎓 JalDrishti — Technical Evaluation & Judge Defense Kit (Q&A)

**Hackathon:** JNTUH Neural Storm 2026 — Green Planet Track (GP-03: Flood and Drought Early Warning System)  
**System:** JalDrishti (జలదృష్టి / जलदृष्टि)  
**Author / Lead Engineer:** Nikhil Kunte (Team Prahar)

---

## Question 1: Why Tabular XGBoost instead of Spatio-Temporal Graph Neural Networks (GNN) or Deep LSTMs?

### 🔬 The Engineering Reality:
1. **The Medium-Data Tabular Regime:**
   - Our 10-year daily climatological dataset (2015–2025) across 4 basin stations contains 15,828 station-day observations (10,228 train, 5,600 test).
   - In tabular datasets with $N < 10^5$ samples and heterogeneous physical dimensions (millimeters of precipitation, cubic meters of discharge, volumetric percentages of soil moisture), deep architectures (LSTMs, GRUs, Temporal Fusion Transformers, GNNs) severely overfit, require extensive regularization, and are hyperparameter-brittle.
   - Rigorous independent benchmarks (*Grinsztajn et al., NeurIPS 2022: "Why do tree-based models still outperform deep learning on tabular data?"*) demonstrate that gradient-boosted decision trees consistently outperform deep neural networks on tabular climate datasets.
2. **Deterministic TreeSHAP Interpretability vs. Neural "Black Boxes":**
   - Frontline district collectors and disaster management authorities cannot order mandatory village evacuations based on uninterpretable neural network hidden states or attention weights (which are post-hoc and frequently unfaithful).
   - XGBoost allows exact, polynomial-time Shapley feature attribution via **TreeSHAP** (*Lundberg et al., Nature Machine Intelligence 2020*). TreeSHAP guarantees local accuracy, missingness, and consistency, allowing JalDrishti to prove mathematically whether an alert is driven by 7-day soil saturation or a sudden 24-hour cloudburst spike.
3. **Severe Kurtosis & Hydraulic Step-Changes:**
   - Monsoonal river discharge exhibits extreme right-skew (base flow of ~5 m³/s jumping to >1,200 m³/s during catastrophic floods). Decision trees split feature space using orthogonal axis-aligned thresholds, making them completely invariant to monotonic transformations, magnitude scaling, or exploding gradients that destabilize neural activation functions.
4. **Edge Deployment Feasibility:**
   - Tree inference executes in **2.33 ms (p50) on a single commodity CPU core**, requiring no GPU accelerators, minimizing capital costs for local district emergency operations centers.

---

## Question 2: How does the system guarantee zero-failure telemetry when network connections drop during extreme monsoons?

### 🛡️ The Dual-Mode Telemetry & Cache Protocol:
Disaster-prone river reaches frequently suffer fiber cuts, cellular tower outages, and power grid failures during peak cyclones and monsoons. JalDrishti implements a multi-tiered fail-safe architecture (`src/telemetry.py`):
1. **Tier 1 (Live Ingestion):**
   - When network connectivity is active, the system fetches live forecasts and river discharge from Open-Meteo & ECMWF GloFAS APIs.
2. **Tier 2 (Disk Cache with 3-Hour TTL):**
   - Ingested payloads are immediately serialized to `data/cache/telemetry_cache.json`.
   - If repeated calls occur within 3 hours, data is served from local disk in `< 1 ms` without external network roundtrips.
3. **Tier 3 (Zero-Exception Offline Fixture Fallback):**
   - If an API returns HTTP 429/500, DNS lookups time out, or the host is completely disconnected, the ingestion wrapper catches all network exceptions and immediately promotes the historical baseline dataset (`data/all_districts.csv`).
4. **Tier 4 (Transparent UI Mode Badging):**
   - The user is never misled about data provenance. Prominent UI status badges explicitly inform operators:
     - `[🟢 LIVE TELEMETRY - OPEN-METEO]`
     - `[🟡 LOCAL CACHE FALLBACK (OFFLINE)]`
     - `[🔵 HISTORICAL REPLAY / SIMULATION]`

---

## Question 3: In public flood early warning, false alarms cause panic, while missed floods cause deaths. How does JalDrishti mathematically manage this trade-off?

### ⚖️ Asymmetric Disaster Loss Optimization ($F_2$-Score):
Traditional machine learning optimizers minimize symmetric cross-entropy or maximize accuracy / $F_1$-score, which treats False Negatives (FN) and False Positives (FP) as having identical real-world cost.

In hydrological disaster management, the costs are radically asymmetric:
- **Cost of a False Negative ($C_{\text{FN}}$):** Catastrophic loss of human life, unevacuated tribal hamlets, drowned cattle, destroyed civil machinery.
- **Cost of a False Positive ($C_{\text{FP}}$):** Temporary precautionary deployment of emergency inspection boats, revenue divisional officer inspections, temporary reservoir gate readiness.
- **Ratio:** $C_{\text{FN}} \gg C_{\text{FP}}$ (empirically estimated at $10:1$ to $50:1$).

### Mathematical Implementation:
1. **Cost-Sensitive Loss:** We apply `scale_pos_weight` during XGBoost training to penalize false negatives during split finding.
2. **Evaluation Metric ($F_2$-Score, $\beta=2$):**
   $$F_2 = 5 \cdot \frac{\text{Precision} \cdot \text{Recall}}{4 \cdot \text{Precision} + \text{Recall}}$$
   The $F_2$-score places **4x more mathematical weight on Recall than Precision**.
3. **Empirical Results (2022–2025 Test Set):**
   - Naive persistence baseline achieves 75.09% recall, missing **144 flood days**.
   - API-3 linear rainfall index triggers **754 false alarms** (precision: 45.12%).
   - JalDrishti's 72h XGBoost model achieves **90.66% Recall (F2: 0.8291)**, capturing **524 out of 578 flood days** and missing only 54 days.
4. **Tiered Public Action Stages:** To prevent public panic from precautionary alerts, warnings are stratified into:
   - *Stage 1 (Advisory)* for moderate probabilities.
   - *Stage 2 (Evacuate Livestock & Low-lying Farms)* for elevated probabilities.
   - *Stage 3 (Mandatory Human Relocation)* only when 72h probability crosses severe danger thresholds.

---

## Question 4: How does JalDrishti interface with physical Central Water Commission (CWC) river gauges and reservoir discharge data?

### 🌊 Gridded Reanalysis vs. In-Situ Calibration:
1. **Current Foundation (Open-Meteo & ECMWF GloFAS):**
   - Historical training (2015–2025) utilizes European Centre for Medium-Range Weather Forecasts (ECMWF) GloFAS gridded hydrological surface reanalysis. This provides standardized, continuous daily discharge without gaps caused by broken physical gauge sensors.
2. **CWC Danger Level Harmonization:**
   - At Bhadrachalam, physical Central Water Commission warning levels are strictly demarcated:
     - 1st Warning Level: 43 feet
     - 2nd Warning Level: 48 feet
     - 3rd / Extreme Danger Level: 53 feet
   - In `models/thresholds.json`, our 95th percentile discharge threshold (108.9 m³/s for Bhadrachalam) aligns statistically with the physical stage-discharge rating curve when water spills beyond normal channel banks.
3. **Modular Gauge Ingestion Pipeline:**
   - In `config/basins.yaml`, each station defines its physical `gauge_id` and localized threshold.
   - When deploying to a DEOC, our modular architecture allows hot-swapping ECMWF gridded discharge with physical CWC Telemetry APIs or State Irrigation Department reservoir outflow reports (e.g., Sriram Sagar, Kadam, and Polavaram discharges) without altering the downstream feature pipeline.

---

## Question 5: Why are Flood and Drought decoupled into separate operational interfaces? Isn't a single "Water Risk Index" simpler?

### ⏱️ Incongruent Hydrological Timescales:
A single aggregated "water score" is dangerous and unscientific because fluvial flooding and agricultural drought operate across completely different physical timescales and atmospheric mechanisms:

| Hydrological Hazard | Physical Driver | Primary Timescale | Operational Action |
| :--- | :--- | :--- | :--- |
| **Rapid Inundation (Flood)** | Cloudburst precipitation, upstream catchment runoff surge, river channel capacity exceedance. | **24 to 72 Hours** | Immediate civil defense evacuation, boat deployment, livestock relocation. |
| **Meteorological & Agricultural Drought** | Prolonged monsoon hiatus, high evapotranspiration, cumulative root-zone moisture depletion. | **30 to 90 Days** | Canal water rationing, contingency crop planning (millets vs paddy), borewell regulation. |

### Operational Separation in JalDrishti:
- **Tab 1 (`Rapid Flood Inundation`):** Focuses exclusively on hourly to 72h river crest dynamics, hydrographs, What-If hydraulic stress-testing, and rapid emergency WhatsApp broadcasts.
- **Tab 2 (`Meteorological & Agricultural Drought`):** Analyzes multi-month Standardized Precipitation Indices (**SPI-1** for 30-day meteorological deficit, **SPI-3** for 90-day agricultural deficit) and **Soil Moisture Z-Score Anomalies** over 24-month rolling trajectories, delivering agronomic contingency plans to Rythu Bharosa Kendras (RBKs).
- Combining them into a single tab creates visual clutter and operational ambiguity for emergency managers. Decoupling them reflects professional hydro-informatics practice.
