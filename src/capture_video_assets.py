"""
JalDrishti - Automated Video-Grade Screenshot Capture Suite
Captures 10 high-resolution (1920x1080), presentation-grade screenshots tailored
specifically for video editing, B-roll cutaways, and executive presentations.
Outputs to docs/screenshots/video_assets/ and packages into JalDrishti_Video_Storyboard_Assets.zip.
"""

import os
import sys
import time
import zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_URL = "http://localhost:8501"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ASSETS_DIR = PROJECT_ROOT / "docs" / "screenshots" / "video_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
ZIP_DEST = PROJECT_ROOT / "docs" / "screenshots" / "JalDrishti_Video_Storyboard_Assets.zip"


def scroll_container_to(page, pixel_y):
    page.evaluate(
        f"""() => {{
        const main = document.querySelector('section.main') || document.querySelector('[data-testid="stMain"]');
        if (main) main.scrollTop = {pixel_y};
        else window.scrollTo(0, {pixel_y});
    }}"""
    )


def scroll_element_into_view(page, locator, block="center"):
    locator.first.evaluate(
        f"el => el.scrollIntoView({{ block: '{block}', behavior: 'instant' }})"
    )


def main():
    print(f"================================================================================")
    print(f"JALDRISHTI: AUTOMATED VIDEO ASSETS CAPTURE SUITE (10 SHOTS)")
    print(f"Target URL: {TARGET_URL} | Output: {ASSETS_DIR}")
    print(f"================================================================================\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_EXE,
            headless=True,
            args=["--disable-web-security", "--allow-running-insecure-content"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.5,  # High-DPI crisp rendering for video
        )
        page = context.new_page()

        print("Navigating to JalDrishti live instance...")
        page.goto(TARGET_URL, wait_until="networkidle")
        page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
        page.wait_for_timeout(3000)

        # Tab locators
        tab_flood = page.locator('[role="tab"]').filter(has_text="Rapid Flood")
        tab_drought = page.locator('[role="tab"]').filter(has_text="Drought")
        tab_audit = page.locator('[role="tab"]').filter(has_text="Model Audit")
        tab_ops = page.locator('[role="tab"]').filter(has_text="Operations")

        # ----------------------------------------------------------------------
        # SHOT 1: 01_brand_header_live_telemetry.png
        # ----------------------------------------------------------------------
        print("[1/10] Capturing: 01_brand_header_live_telemetry.png")
        tab_flood.click()
        page.wait_for_timeout(1000)
        scroll_container_to(page, 0)
        page.wait_for_timeout(1200)

        s1_path = ASSETS_DIR / "01_brand_header_live_telemetry.png"
        page.screenshot(path=str(s1_path))
        print(f"  -> Saved: {s1_path.name} ({s1_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 2: 02_interactive_basin_map_shelters.png
        # ----------------------------------------------------------------------
        print("[2/10] Capturing: 02_interactive_basin_map_shelters.png")
        tab_flood.click()
        page.wait_for_timeout(1000)
        scroll_container_to(page, 180)
        page.wait_for_timeout(2000)

        s2_path = ASSETS_DIR / "02_interactive_basin_map_shelters.png"
        page.screenshot(path=str(s2_path))
        print(f"  -> Saved: {s2_path.name} ({s2_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 3: 03_scenario_presets_interactive.png
        # ----------------------------------------------------------------------
        print("[3/10] Capturing: 03_scenario_presets_interactive.png")
        tab_flood.click()
        page.wait_for_timeout(800)
        scroll_element_into_view(page, page.locator('h5:has-text("Interactive Scenario Sandbox")'), block="start")
        page.wait_for_timeout(1500)

        s3_path = ASSETS_DIR / "03_scenario_presets_interactive.png"
        page.screenshot(path=str(s3_path))
        print(f"  -> Saved: {s3_path.name} ({s3_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 4: 04_stress_test_critical_spike.png
        # ----------------------------------------------------------------------
        print("[4/10] Capturing: 04_stress_test_critical_spike.png")
        btn_preset_peak = page.locator('button:has-text("July 2022 Peak Crest")').first
        btn_preset_peak.click()
        page.wait_for_timeout(2000)

        scroll_element_into_view(page, page.locator('div.jd-card:has-text("Simulated 72h Probability")'), block="center")
        page.wait_for_timeout(1200)

        s4_path = ASSETS_DIR / "04_stress_test_critical_spike.png"
        page.screenshot(path=str(s4_path))
        print(f"  -> Saved: {s4_path.name} ({s4_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 5: 05_explain_like_farmer_trilingual.png
        # ----------------------------------------------------------------------
        print("[5/10] Capturing: 05_explain_like_farmer_trilingual.png")
        scroll_element_into_view(page, page.locator('[data-testid="stExpander"]'), block="center")
        page.wait_for_timeout(1500)

        s5_path = ASSETS_DIR / "05_explain_like_farmer_trilingual.png"
        page.screenshot(path=str(s5_path))
        print(f"  -> Saved: {s5_path.name} ({s5_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 6: 06_whatsapp_dispatch_copy_tabs.png
        # ----------------------------------------------------------------------
        print("[6/10] Capturing: 06_whatsapp_dispatch_copy_tabs.png")
        scroll_element_into_view(page, page.locator('div.whatsapp-container'), block="start")
        page.wait_for_timeout(1200)

        s6_path = ASSETS_DIR / "06_whatsapp_dispatch_copy_tabs.png"
        page.screenshot(path=str(s6_path))
        print(f"  -> Saved: {s6_path.name} ({s6_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 7: 07_tactical_incident_download.png
        # ----------------------------------------------------------------------
        print("[7/10] Capturing: 07_tactical_incident_download.png")
        scroll_element_into_view(page, page.locator('button:has-text("Download 1-Page Incident Summary")'), block="center")
        page.wait_for_timeout(1200)

        s7_path = ASSETS_DIR / "07_tactical_incident_download.png"
        page.screenshot(path=str(s7_path))
        print(f"  -> Saved: {s7_path.name} ({s7_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 8: 08_drought_spi_gamma_analysis.png
        # ----------------------------------------------------------------------
        print("[8/10] Capturing: 08_drought_spi_gamma_analysis.png")
        tab_drought.click()
        page.wait_for_timeout(2500)
        scroll_container_to(page, 0)
        page.wait_for_timeout(1500)

        s8_path = ASSETS_DIR / "08_drought_spi_gamma_analysis.png"
        page.screenshot(path=str(s8_path))
        print(f"  -> Saved: {s8_path.name} ({s8_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 9: 09_model_audit_baseline_metrics.png
        # ----------------------------------------------------------------------
        print("[9/10] Capturing: 09_model_audit_baseline_metrics.png")
        tab_audit.click()
        page.wait_for_timeout(2500)
        scroll_element_into_view(page, page.locator('h4:has-text("Quantitative Performance")'), block="start")
        page.wait_for_timeout(1500)

        s9_path = ASSETS_DIR / "09_model_audit_baseline_metrics.png"
        page.screenshot(path=str(s9_path))
        print(f"  -> Saved: {s9_path.name} ({s9_path.stat().st_size / 1024:.1f} KB)")

        # ----------------------------------------------------------------------
        # SHOT 10: 10_enterprise_architecture_b2g.png
        # ----------------------------------------------------------------------
        print("[10/10] Capturing: 10_enterprise_architecture_b2g.png")
        tab_ops.click()
        page.wait_for_timeout(2500)
        scroll_container_to(page, 0)
        page.wait_for_timeout(1500)

        s10_path = ASSETS_DIR / "10_enterprise_architecture_b2g.png"
        page.screenshot(path=str(s10_path))
        print(f"  -> Saved: {s10_path.name} ({s10_path.stat().st_size / 1024:.1f} KB)")

        browser.close()

    # Packaging into ZIP
    print(f"\nPackaging all 10 video screenshots into: {ZIP_DEST}")
    with zipfile.ZipFile(ZIP_DEST, "w", zipfile.ZIP_DEFLATED) as zipf:
        for img_file in sorted(ASSETS_DIR.glob("*.png")):
            zipf.write(img_file, arcname=img_file.name)
            print(f"  + Added to zip: {img_file.name}")

    print(f"\n[SUCCESS] ZIP Archive created: {ZIP_DEST} ({ZIP_DEST.stat().st_size / (1024 * 1024):.2f} MB)")
    print("ALL 10 VIDEO-GRADE SCREENSHOTS CAPTURED AND BUNDLED CLEANLY!\n")


if __name__ == "__main__":
    main()
