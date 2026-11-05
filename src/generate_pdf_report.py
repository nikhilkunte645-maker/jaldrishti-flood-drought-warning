import base64
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SCREENSHOTS_DIR = DOCS_DIR / "screenshots"
OUTPUT_PDF = DOCS_DIR / "JalDrishti_Hackathon_Submission_Report.pdf"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def get_base64_image(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def generate_pdf():
    print("Preparing assets for publication-grade PDF compilation...")
    logo = get_base64_image(DOCS_DIR / "assets" / "logo.png")
    img1 = get_base64_image(SCREENSHOTS_DIR / "01_risk_dashboard_overview.png")
    img2 = get_base64_image(SCREENSHOTS_DIR / "02_whatif_scenario_sandbox.png")
    img3 = get_base64_image(SCREENSHOTS_DIR / "03_vernacular_alert_telugu.png")
    img4 = get_base64_image(SCREENSHOTS_DIR / "04_model_metrics_f2_loss.png")
    img5 = get_base64_image(SCREENSHOTS_DIR / "05_explainable_ai_shap.png")
    img6 = get_base64_image(SCREENSHOTS_DIR / "06_backtest_july2022_flood.png")

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>JalDrishti - Project Submission Report</title>
<style>
    @page {
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        line-height: 1.55;
        font-size: 9.5pt;
        margin: 0;
        padding: 0;
        background-color: #ffffff;
    }

    .header-banner {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
        color: #ffffff;
        padding: 22px 26px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .header-banner h1 {
        margin: 0 0 6px 0;
        font-size: 22pt;
        letter-spacing: -0.5px;
        color: #38bdf8;
    }

    .header-banner .tagline {
        font-size: 10.5pt;
        color: #e2e8f0;
        margin-bottom: 12px;
        font-weight: 400;
    }

    .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px 16px;
        font-size: 8.5pt;
        border-top: 1px solid #334155;
        padding-top: 10px;
        color: #94a3b8;
    }

    .meta-grid strong {
        color: #f8fafc;
    }

    .meta-grid a {
        color: #38bdf8;
        text-decoration: none;
    }

    h2 {
        color: #0f172a;
        font-size: 13pt;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
        margin-top: 22px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }

    h3 {
        color: #1e3a8a;
        font-size: 11pt;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 10px 0;
        text-align: justify;
    }

    .highlight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 12px 0;
        font-size: 9pt;
    }

    .stat-card-row {
        display: flex;
        gap: 12px;
        margin: 12px 0;
    }

    .stat-card {
        flex: 1;
        background: #f1f5f9;
        border-radius: 8px;
        padding: 10px 12px;
        text-align: center;
        border: 1px solid #cbd5e1;
    }

    .stat-val {
        font-size: 15pt;
        font-weight: 700;
        color: #0369a1;
        margin-bottom: 2px;
    }

    .stat-lbl {
        font-size: 7.5pt;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 8pt;
    }

    th, td {
        border: 1px solid #cbd5e1;
        padding: 5px 8px;
        text-align: left;
    }

    th {
        background-color: #0f172a;
        color: #ffffff;
        font-weight: 600;
        text-align: center;
    }

    tr:nth-child(even) {
        background-color: #f8fafc;
    }

    .num-col {
        text-align: right;
    }

    .center-col {
        text-align: center;
    }

    .highlight-row {
        background-color: #e0f2fe !important;
        font-weight: 600;
        color: #0369a1;
    }

    .figure-container {
        margin: 14px 0;
        text-align: center;
        page-break-inside: avoid;
    }

    .figure-img {
        width: 100%;
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .figure-caption {
        font-size: 8pt;
        color: #475569;
        margin-top: 5px;
        font-style: italic;
    }

    .page-break {
        page-break-before: always;
    }

    .badge-pill {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 9999px;
        font-size: 7pt;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-blue { background: #e0f2fe; color: #0369a1; }
    .badge-amber { background: #fef3c7; color: #b45309; }
    .badge-red { background: #fee2e2; color: #b91c1c; }

    ul, ol {
        margin: 0 0 10px 0;
        padding-left: 18px;
    }

    li {
        margin-bottom: 3px;
    }
</style>
</head>
<body>

<!-- PAGE 1: TITLE & EXECUTIVE SUMMARY -->
<div class="header-banner">
    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 12px;">
        <img src="{{LOGO}}" style="width: 58px; height: 58px; border-radius: 12px; box-shadow: 0 4px 14px rgba(0, 242, 254, 0.35); background: #0b132b; flex-shrink: 0;" alt="Logo">
        <div>
            <h1 style="margin: 0; line-height: 1.1;">JalDrishti (జలదృష్టి / जलदृष्टि)</h1>
            <div class="tagline" style="margin-top: 4px; margin-bottom: 0;">Hyper-Localized, Explainable Flood & Drought Early Warning System for the Godavari Basin</div>
        </div>
    </div>
    <div class="meta-grid">
        <div><strong>Hackathon:</strong> JNTUH Neural Storm 2026</div>
        <div><strong>Track:</strong> Green Planet (GP-03: Flood & Drought Early Warning)</div>
        <div><strong>Author & Lead Engineer:</strong> Nikhil Kunte</div>
        <div><strong>Live Cloud Deployment:</strong> <a href="https://jaldrishti-warning.streamlit.app">jaldrishti-warning.streamlit.app</a></div>
        <div><strong>GitHub Repository:</strong> <a href="https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning">github.com/.../jaldrishti-flood-drought-warning</a></div>
        <div><strong>Spatial Scope:</strong> Godavari Basin, Telangana (4 Monitored Districts)</div>
    </div>
</div>

<h2>1. Executive Summary & Problem Statement</h2>
<p>
The Godavari river basin in Telangana represents one of India's most ecologically vital yet hydrologically volatile river catchments. Every monsoon, communities along the downstream Godavari reach face severe, life-threatening flooding. In July 2022, river levels at Bhadrachalam (Bhadradri Kothagudem) breached the highest 3rd danger level (53 ft) and peaked near an unprecedented 71.3 ft, inundating over 70 revenue villages and displacing more than 25,000 citizens. Conversely, during pre-monsoon summer months, rapid soil moisture depletion and rainfall deficits trigger intense agricultural droughts, crippling paddy and cotton cultivation.
</p>
<p>
Existing centralized regional alerts suffer from two systemic failures: (1) <strong>Spatial Imprecision</strong> (district-wide blanket warnings that fail to capture river reach hydraulics), and (2) <strong>Linguistic Inaccessibility</strong> (complex technical bulletins that cannot be immediately digested by local gram panchayats and rural farmers).
</p>
<p>
<strong>JalDrishti</strong> solves both bottlenecks. It is a full-stack, air-gapped hydrological intelligence platform combining cost-sensitive machine learning (XGBoost), climatological Standardized Precipitation Indices (SPI), local TreeSHAP attribution, and instant vernacular emergency dispatches validated against official Telangana State Disaster Management Authority (TGSDMA) protocols.
</p>

<div class="stat-card-row">
    <div class="stat-card">
        <div class="stat-val">90.66%</div>
        <div class="stat-lbl">72h Flood Recall</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">0.8291</div>
        <div class="stat-lbl">72h F2-Score</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">7 Days</div>
        <div class="stat-lbl">Catchment Precursor Warning</div>
    </div>
    <div class="stat-card">
        <div class="stat-val">100%</div>
        <div class="stat-lbl">Air-Gapped Local Runtime</div>
    </div>
</div>

<h2>2. System Architecture & Technical Specifications</h2>
<p>
JalDrishti is designed for maximum operational reliability under extreme power and network stress. The platform strictly enforces zero external API calls at runtime, loading pre-compiled, serialized artifacts locally:
</p>
<ul>
    <li><strong>Data Pipeline:</strong> Ingested 10 years (2015–2025) of daily precipitation, 2m mean temperature, 0–7cm volumetric soil moisture, and calibrated river discharge for 4 key Godavari districts: <em>Bhadradri Kothagudem</em> (Bhadrachalam reach), <em>Mulugu</em> (Ramappa / Eturnagaram), <em>Nizamabad</em> (Sriram Sagar Dam), and <em>Adilabad</em> (Kadam / upper reach).</li>
    <li><strong>Predictive Engine:</strong> Horizon-specific Gradient Boosted Trees (XGBoost) predicting flood probabilities within 24h, 48h, and 72h windows. Models incorporate rolling rainfall accumulation (1d, 3d, 7d, 14d), upstream discharge lag states (t-1, t-2, t-3), river surge velocity, and upper-catchment soil moisture wetting rates.</li>
    <li><strong>Dual-Hazard Climatology:</strong> Computes 1-month and 3-month Standardized Precipitation Indices (SPI-1, SPI-3) via Gamma distribution parameter fitting, accompanied by calendar-month Soil Moisture Z-score anomalies.</li>
    <li><strong>Air-Gapped Safety:</strong> Fully self-contained local caching; app cold-starts in &lt;1.5s with zero telemetry overhead.</li>
</ul>

<!-- PAGE BREAK: VISUAL ANNEX 1 -->
<div class="page-break"></div>

<h2>3. Risk Dashboard & Real-Time Monitoring</h2>
<p>
The JalDrishti interactive dashboard provides disaster authorities with immediate multi-hazard situational awareness. The integrated GIS module renders interactive Leaflet circle markers color-coded by real-time risk level, paired with a live hydro-meteorological sensor snapshot and forward probability matrices.
</p>

<div class="figure-container">
    <img src="{{IMG1}}" class="figure-img" alt="Risk Dashboard Overview">
    <div class="figure-caption">Figure 1: JalDrishti Primary Risk Dashboard — Displaying spatial network markers across Telangana's Godavari basin, real-time hydrological snapshot at Bhadrachalam, and the 24h/48h/72h early warning horizon matrix.</div>
</div>

<div class="highlight-card">
    <b>Key Dashboard Features:</b>
    <ul>
        <li><strong>Reach-Specific Flood Thresholds:</strong> Dynamic 95th percentile baseline calculated strictly from historical training years (e.g., 80.9 m³/s for Bhadrachalam).</li>
        <li><strong>Multi-Horizon Probability Gauge:</strong> Concurrent 24-hour, 48-hour, and 72-hour flood risk cards with color-coded risk tier badges.</li>
        <li><strong>Climatological Drought Monitor:</strong> Real-time SPI-1, SPI-3, and Soil Moisture Z-Score classification (Normal / Moderate / Severe).</li>
    </ul>
</div>

<!-- PAGE BREAK: ASYMMETRIC LOSS & F2 BENCHMARKING -->
<div class="page-break"></div>

<h2>4. Quantitative Model Evaluation & Asymmetric Disaster Loss (F2-Score)</h2>
<p>
All machine learning models are evaluated out-of-time on unseen test data (2022–2025). We benchmark JalDrishti against two standard baselines: (1) <strong>Naive Persistence Baseline</strong> ("tomorrow equals today"), and (2) an <strong>Antecedent Precipitation Index (API-3 Linear Benchmark)</strong> (P<sub>t</sub> + 0.8 P<sub>t-1</sub> + 0.6 P<sub>t-2</sub>).
</p>

<h3>The Asymmetric Disaster Loss Function</h3>
<p>
In disaster early warning, error consequences are fundamentally asymmetric:
</p>
<div class="highlight-card">
    <strong>Loss Asymmetry Justification:</strong>
    <p style="margin: 4px 0 0 0;">
    A <strong>False Negative</strong> (a missed flood event) results in unevacuated human settlements, loss of human life, livestock destruction, and infrastructure failure. A <strong>False Positive</strong> (a precautionary false alarm) merely triggers preventative embankment inspections and emergency team standby. 
    Therefore, disaster management models must maximize <strong>Recall</strong> over Precision. We mathematically formalize this objective using the <strong>F2-Score</strong> (&beta; = 2), which weights Recall <strong>4 times more heavily</strong> than Precision:
    <br><br>
    <center><strong>F<sub>2</sub> = (1 + 2<sup>2</sup>) &times; (Precision &times; Recall) / ((2<sup>2</sup> &times; Precision) + Recall) = 5 &times; (Precision &times; Recall) / (4 &times; Precision + Recall)</strong></center>
    </p>
</div>

<h3>Out-of-Time Performance Comparison (2022–2025 Test Set)</h3>
<table>
    <thead>
        <tr>
            <th>Horizon</th>
            <th>Model / Benchmark</th>
            <th>Precision</th>
            <th>Recall</th>
            <th>F1-Score</th>
            <th>F2-Score</th>
            <th>ROC-AUC</th>
            <th>False Alarms (FP)</th>
            <th>Missed Floods (FN)</th>
        </tr>
    </thead>
    <tbody>
        <tr class="highlight-row">
            <td class="center-col"><strong>24h</strong></td>
            <td><strong>JalDrishti (XGBoost)</strong></td>
            <td class="num-col">78.50%</td>
            <td class="num-col"><strong>94.70%</strong></td>
            <td class="num-col">85.84%</td>
            <td class="num-col"><strong>90.95%</strong></td>
            <td class="num-col"><strong>0.9935</strong></td>
            <td class="num-col">150</td>
            <td class="num-col"><strong>30</strong></td>
        </tr>
        <tr>
            <td class="center-col">24h</td>
            <td>Naive Persistence</td>
            <td class="num-col">88.94%</td>
            <td class="num-col">88.75%</td>
            <td class="num-col">88.84%</td>
            <td class="num-col">88.79%</td>
            <td class="num-col">0.5000</td>
            <td class="num-col">53</td>
            <td class="num-col">54</td>
        </tr>
        <tr>
            <td class="center-col">24h</td>
            <td>API-3 Linear Benchmark</td>
            <td class="num-col">30.05%</td>
            <td class="num-col">71.25%</td>
            <td class="num-col">42.27%</td>
            <td class="num-col">55.92%</td>
            <td class="num-col">0.8752</td>
            <td class="num-col">796</td>
            <td class="num-col">138</td>
        </tr>
        <tr class="highlight-row">
            <td class="center-col"><strong>48h</strong></td>
            <td><strong>JalDrishti (XGBoost)</strong></td>
            <td class="num-col">70.93%</td>
            <td class="num-col"><strong>92.35%</strong></td>
            <td class="num-col">80.24%</td>
            <td class="num-col"><strong>87.06%</strong></td>
            <td class="num-col"><strong>0.9859</strong></td>
            <td class="num-col">218</td>
            <td class="num-col"><strong>44</strong></td>
        </tr>
        <tr>
            <td class="center-col">48h</td>
            <td>Naive Persistence</td>
            <td class="num-col">90.59%</td>
            <td class="num-col">81.24%</td>
            <td class="num-col">85.66%</td>
            <td class="num-col">82.95%</td>
            <td class="num-col">0.5000</td>
            <td class="num-col">45</td>
            <td class="num-col">100</td>
        </tr>
        <tr>
            <td class="center-col">48h</td>
            <td>API-3 Linear Benchmark</td>
            <td class="num-col">34.08%</td>
            <td class="num-col">73.92%</td>
            <td class="num-col">46.65%</td>
            <td class="num-col">59.91%</td>
            <td class="num-col">0.8871</td>
            <td class="num-col">762</td>
            <td class="num-col">139</td>
        </tr>
        <tr class="highlight-row">
            <td class="center-col"><strong>72h</strong></td>
            <td><strong>JalDrishti (XGBoost)</strong></td>
            <td class="num-col">62.79%</td>
            <td class="num-col"><strong>90.66%</strong></td>
            <td class="num-col">74.19%</td>
            <td class="num-col"><strong>82.91%</strong></td>
            <td class="num-col"><strong>0.9766</strong></td>
            <td class="num-col">309</td>
            <td class="num-col"><strong>54</strong></td>
        </tr>
        <tr>
            <td class="center-col">72h</td>
            <td>Naive Persistence</td>
            <td class="num-col">87.56%</td>
            <td class="num-col">75.09%</td>
            <td class="num-col">80.84%</td>
            <td class="num-col">77.28%</td>
            <td class="num-col">0.5000</td>
            <td class="num-col">61</td>
            <td class="num-col">144</td>
        </tr>
        <tr>
            <td class="center-col">72h</td>
            <td>API-3 Linear Benchmark</td>
            <td class="num-col">37.05%</td>
            <td class="num-col">74.91%</td>
            <td class="num-col">49.58%</td>
            <td class="num-col">61.87%</td>
            <td class="num-col">0.7915</td>
            <td class="num-col">754</td>
            <td class="num-col">145</td>
        </tr>
    </tbody>
</table>

<div class="figure-container">
    <img src="{{IMG4}}" class="figure-img" alt="Model Metrics and F2 Loss Justification">
    <div class="figure-caption">Figure 2: JalDrishti Model Performance Audit Tab — Highlighting out-of-time test metrics, F2-Score validation, and operational trade-off diagnostics.</div>
</div>

<!-- PAGE BREAK: BACKTEST & SCIENTIFIC FRAMING -->
<div class="page-break"></div>

<h2>5. Scientific Backtest: July 2022 Godavari Flood Replay</h2>
<p>
To prevent methodological over-claims, we establish a rigorous hydrological distinction between the model's <strong>forward target window (72 hours)</strong> and the <strong>sustained catchment precursor warning duration</strong>.
</p>

<div class="highlight-card">
    <strong>Scientific Lead-Time Framing:</strong>
    <p style="margin: 4px 0 0 0;">
    <strong>Catchment Saturation Precursor: 7 Days (168 Hours) Prior to Peak Discharge (Target Horizon: 72h Forward Window).</strong><br>
    While the ML model predicts flood probability within a 72-hour forward rolling window, persistent upstream monsoon precipitation and upper-catchment soil moisture saturation caused continuous High-Risk alerts (P &ge; 60%) to trigger starting <strong>July 7, 2022 (P = 72.34%)</strong>. This provided emergency authorities with <strong>7 full calendar days (168 hours)</strong> of sustained precursor warning before the river reached its historic peak crest of <strong>193.98 m³/s</strong> on <strong>July 14, 2022</strong>.
    </p>
</div>

<div class="figure-container">
    <img src="{{IMG6}}" class="figure-img" alt="July 2022 Historic Flood Backtest">
    <div class="figure-caption">Figure 3: Historical Backtest Hydrograph Replay — Demonstrating the 7-day precursor alert line (green) preceding the peak discharge crest (red dashed) on July 14, 2022 at Bhadrachalam.</div>
</div>

<!-- PAGE BREAK: WHAT-IF SIMULATOR & TREESHAP -->
<div class="page-break"></div>

<h2>6. Interactive What-If Scenario Sandbox</h2>
<p>
The <strong>Interactive Scenario Sandbox</strong> empowers disaster managers to stress-test hydraulic thresholds in real-time. By dynamically varying 24-hour rainfall (0–300 mm), river discharge (0–400 m³/s), and soil moisture (10%–100%), operators execute instant air-gapped inference against the loaded XGBoost models to generate immediate operational evacuation advisories.
</p>

<div class="figure-container">
    <img src="{{IMG2}}" class="figure-img" alt="Interactive Scenario Sandbox">
    <div class="figure-caption">Figure 4: Scenario Sandbox Simulator — Live execution with 125mm rainfall and 150m³/s discharge producing an instant 94.5% High-Risk probability and evacuation protocol.</div>
</div>

<h2>7. Explainable AI: Local TreeSHAP Feature Attribution</h2>
<p>
Black-box predictions are dangerous in emergency logistics. JalDrishti integrates <strong>TreeSHAP (SHapley Additive exPlanations)</strong> to provide complete transparency into feature contributions for every forecast. Operators can inspect exactly which physical factors (e.g., 7-day cumulative rainfall vs. antecedent soil saturation) are elevating or suppressing the flood log-odds.
</p>

<div class="figure-container">
    <img src="{{IMG5}}" class="figure-img" alt="Explainable AI TreeSHAP Attribution">
    <div class="figure-caption">Figure 5: TreeSHAP Feature Attribution Bar Chart — Demonstrating transparent physical driver decomposition for Bhadrachalam flood forecasting.</div>
</div>

<!-- PAGE BREAK: VERNACULAR ALERTS & CONCLUSION -->
<div class="page-break"></div>

<h2>8. Grassroots Vernacular Emergency Dispatches</h2>
<p>
To close the critical "last-mile" communication gap, JalDrishti automatically synthesizes mathematical probabilities into localized, WhatsApp-ready emergency dispatches in <strong>English</strong>, <strong>Telugu (తెలుగు)</strong>, and <strong>Hindi (हिन्दी)</strong>. All alert templates are aligned with official <strong>NDMA / TGSDMA</strong> emergency phraseology.
</p>

<div class="figure-container">
    <img src="{{IMG3}}" class="figure-img" alt="Vernacular Alert Broadcast in Telugu">
    <div class="figure-caption">Figure 6: WhatsApp-Style Vernacular Alert Dispatch — Official TGSDMA emergency advisory rendered in native Telugu script for immediate dissemination to village panchayats.</div>
</div>

<h2>9. Hackathon Submission Compliance Checklist</h2>
<table>
    <thead>
        <tr>
            <th>Module</th>
            <th>Requirement Specification</th>
            <th>Status</th>
            <th>Verification Detail</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Module 1</strong></td>
            <td>Scientific Lead-Time Framing</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>Reframed as 7-Day Precursor Saturation (72h forward horizon).</td>
        </tr>
        <tr>
            <td><strong>Module 2</strong></td>
            <td>API-3 Benchmark & F2 Loss</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>Added API-3 linear baseline; achieved 82.91% F2 vs 77.78% baseline.</td>
        </tr>
        <tr>
            <td><strong>Module 3</strong></td>
            <td>Interactive Scenario Sandbox</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>Air-gapped live inference with 4 sliders, risk badge, and advisory.</td>
        </tr>
        <tr>
            <td><strong>Module 4</strong></td>
            <td>Certified Vernacular Alerts</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>72 alert permutations validated with official TGSDMA/NDMA strings.</td>
        </tr>
        <tr>
            <td><strong>Module 5</strong></td>
            <td>Documentation & Git Sync</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>Updated README, demo script, checklist; clean push to main.</td>
        </tr>
        <tr>
            <td><strong>Visuals</strong></td>
            <td>1920x1080 High-DPI Screenshots</td>
            <td class="center-col"><span class="badge-pill badge-green">VERIFIED</span></td>
            <td>Captured 6 presentation-grade screenshots in docs/screenshots/.</td>
        </tr>
    </tbody>
</table>

<div class="highlight-card" style="text-align: center; margin-top: 24px;">
    <strong>JalDrishti (జలదృష్టి / जलदृष्टि)</strong> — Developed solo by <strong>Nikhil Kunte</strong> for JNTUH Neural Storm 2026.<br>
    Live Application: <a href="https://jaldrishti-warning.streamlit.app">https://jaldrishti-warning.streamlit.app</a> • Repository: <a href="https://github.com/nikhilkunte645-maker/jaldrishti-flood-drought-warning">GitHub (Main Branch)</a>
</div>

</body>
</html>
"""

    html_content = (
        html_template
        .replace("{{LOGO}}", logo)
        .replace("{{IMG1}}", img1)
        .replace("{{IMG2}}", img2)
        .replace("{{IMG3}}", img3)
        .replace("{{IMG4}}", img4)
        .replace("{{IMG5}}", img5)
        .replace("{{IMG6}}", img6)
    )

    print("Compiling PDF with Playwright Chromium...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_EXE,
            headless=True
        )
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        page.pdf(
            path=str(OUTPUT_PDF),
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "right": "14mm",
                "bottom": "15mm",
                "left": "14mm",
            },
            display_header_footer=True,
            header_template="<span></span>",
            footer_template="""
                <div style="font-size: 8pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 14mm; font-family: sans-serif;">
                    JalDrishti • JNTUH Neural Storm 2026 • Page <span class="pageNumber"></span> of <span class="totalPages"></span>
                </div>
            """
        )
        browser.close()

    print(f"\n[SUCCESS] PDF generated at: {OUTPUT_PDF}")
    file_size_mb = OUTPUT_PDF.stat().st_size / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    generate_pdf()
