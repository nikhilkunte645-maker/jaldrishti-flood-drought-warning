import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path("docs/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TARGET_URL = "http://localhost:8501"


def set_slider_value(page, label_pattern, target_val):
    sl = page.locator('div[data-testid="stSlider"]').filter(has_text=label_pattern)
    input_elem = sl.locator('input[type="range"]')
    input_elem.evaluate(
        """(el, val) => {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(el, val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    }""",
        target_val,
    )


def select_dropdown_option(page, label_pattern, option_text):
    sb = page.locator('div[data-testid="stSelectbox"]').filter(has_text=label_pattern)
    sb.locator('button[aria-label="Open"]').click()
    page.wait_for_timeout(600)
    opt = page.locator('[role="option"]').filter(has_text=option_text).first
    opt.click()
    page.wait_for_timeout(1000)


def scroll_container_to(page, pixel_y):
    page.evaluate(
        f"""() => {{
        const main = document.querySelector('section.main') || document.querySelector('[data-testid="stMain"]');
        if (main) main.scrollTop = {pixel_y};
        else window.scrollTo(0, {pixel_y});
    }}"""
    )


def main():
    print(f"Starting High-Res (1920x1080) Screenshot Capture Suite against {TARGET_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_EXE, headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.5,  # High-DPI crisp rendering
        )
        page = context.new_page()

        # ======================================================================
        # SCREENSHOT 1: OVERVIEW & INTERACTIVE MAP (RAPID FLOOD INUNDATION)
        # ======================================================================
        print("\n--- [1/6] Capturing: Risk Dashboard Overview & Map ---")
        page.goto(TARGET_URL, wait_until="networkidle")
        page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)

        tab_flood = page.locator('[role="tab"]').filter(has_text="Rapid Flood")
        tab_flood.click()
        page.wait_for_timeout(4000)  # Wait for Folium map iframe and metrics to paint
        scroll_container_to(page, 0)
        page.wait_for_timeout(800)

        ss1_path = OUTPUT_DIR / "01_risk_dashboard_overview.png"
        page.screenshot(path=str(ss1_path))
        print(f"[OK] Saved {ss1_path}")

        # ======================================================================
        # SCREENSHOT 2: INTERACTIVE SCENARIO SANDBOX (LIVE WHAT-IF SIMULATOR)
        # ======================================================================
        print("\n--- [2/6] Capturing: What-If Scenario Sandbox ---")
        tab_flood.click()
        page.wait_for_timeout(1000)

        # Set sliders: Simulated Rain ~125.0, Current River Discharge ~150.0
        set_slider_value(page, "Simulated 24h Rainfall", 125.0)
        page.wait_for_timeout(400)
        set_slider_value(page, "Current River Discharge", 150.0)
        page.wait_for_timeout(400)
        set_slider_value(page, "Volumetric Soil Moisture", 65.0)
        page.wait_for_timeout(400)

        # Click Run Live Hydraulic Inference
        btn_infer = page.locator('button:has-text("Run Live Hydraulic Inference")')
        btn_infer.click()
        page.wait_for_selector('text="HIGH RISK"', timeout=10000)
        page.wait_for_timeout(1000)

        # Scroll so the Scenario Sandbox starts at the very top of viewport
        page.locator('h5:has-text("Interactive Scenario Sandbox")').evaluate(
            "el => el.scrollIntoView({ block: 'start', behavior: 'instant' })"
        )
        page.wait_for_timeout(1000)

        ss2_path = OUTPUT_DIR / "02_whatif_scenario_sandbox.png"
        page.screenshot(path=str(ss2_path))
        print(f"[OK] Saved {ss2_path}")

        # ======================================================================
        # SCREENSHOT 3: GRASSROOTS VERNACULAR ALERTS (TELUGU)
        # ======================================================================
        print("\n--- [3/6] Capturing: Vernacular Alerts (Telugu Broadcast) ---")
        select_dropdown_option(page, "Vernacular Alert Language", "తెలుగు")
        page.wait_for_timeout(2000)

        scroll_container_to(page, 0)
        page.wait_for_timeout(1000)

        ss3_path = OUTPUT_DIR / "03_vernacular_alert_telugu.png"
        page.screenshot(path=str(ss3_path))
        print(f"[OK] Saved {ss3_path}")

        # Reset language back to English
        select_dropdown_option(page, "Vernacular Alert Language", "English")
        page.wait_for_timeout(1500)

        # ======================================================================
        # SCREENSHOT 4: MODEL EVALUATION & F2-SCORE BENCHMARK TABLE
        # ======================================================================
        print("\n--- [4/6] Capturing: Model Evaluation & F2-Score Benchmark Table ---")
        tab_audit = page.locator('[role="tab"]').filter(has_text="Model Audit")
        tab_audit.click()
        page.wait_for_timeout(2500)

        # Scroll to quantitative benchmark section
        page.locator('h4:has-text("Quantitative Performance")').evaluate(
            "el => el.scrollIntoView({ block: 'start', behavior: 'instant' })"
        )
        page.wait_for_timeout(1000)

        ss4_path = OUTPUT_DIR / "04_model_metrics_f2_loss.png"
        page.screenshot(path=str(ss4_path))
        print(f"[OK] Saved {ss4_path}")

        # ======================================================================
        # SCREENSHOT 5: EXPLAINABLE AI (TREESHAP ATTRIBUTION)
        # ======================================================================
        print("\n--- [5/6] Capturing: Explainable AI (TreeSHAP Attribution) ---")
        tab_flood.click()
        page.wait_for_timeout(2000)

        # Scroll so the TreeSHAP section starts at top of viewport
        page.locator('h5:has-text("Why this risk")').evaluate(
            "el => el.scrollIntoView({ block: 'start', behavior: 'instant' })"
        )
        page.wait_for_timeout(1500)

        ss5_path = OUTPUT_DIR / "05_explainable_ai_shap.png"
        page.screenshot(path=str(ss5_path))
        print(f"[OK] Saved {ss5_path}")

        # ======================================================================
        # SCREENSHOT 6: HISTORICAL BACKTEST: JULY 2022 GODAVARI FLOOD
        # ======================================================================
        print("\n--- [6/6] Capturing: Historical Backtest (July 2022 Flood) ---")
        tab_audit.click()
        page.wait_for_timeout(2000)

        scroll_container_to(page, 0)
        page.wait_for_timeout(2500)  # Wait for backtest HTML iframe to render

        ss6_path = OUTPUT_DIR / "06_backtest_july2022_flood.png"
        page.screenshot(path=str(ss6_path))
        print(f"[OK] Saved {ss6_path}")

        browser.close()
        print("\n✨ ALL 6 PRESENTATION-GRADE SCREENSHOTS CAPTURED SUCCESSFULLY! ✨")


if __name__ == "__main__":
    main()
