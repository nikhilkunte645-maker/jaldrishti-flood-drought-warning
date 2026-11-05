"""
JalDrishti - Asset Integrity & Link Audit Script
Verifies all project assets, PDF reports, screenshots, ZIP archives, and markdown links across repository.
"""

import os
import re
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Required individual asset files
CRITICAL_ASSETS = [
    PROJECT_ROOT / "docs" / "assets" / "logo.png",
    PROJECT_ROOT / "docs" / "JalDrishti_Hackathon_Submission_Report.pdf",
    PROJECT_ROOT / "docs" / "metrics_summary.json",
    PROJECT_ROOT / "docs" / "PITCH_DECK.md",
    PROJECT_ROOT / "docs" / "FINAL_SUBMISSION.md",
    PROJECT_ROOT / "docs" / "screenshots" / "JalDrishti_Video_Storyboard_Assets.zip",
]

# Required 6 original UI screenshots
ORIGINAL_SCREENSHOTS = [
    "01_risk_dashboard_overview.png",
    "02_whatif_scenario_sandbox.png",
    "03_vernacular_alert_telugu.png",
    "04_model_metrics_f2_loss.png",
    "05_explainable_ai_shap.png",
    "06_backtest_july2022_flood.png",
]

# Required 10 video asset screenshots
VIDEO_SCREENSHOTS = [
    "01_brand_header_live_telemetry.png",
    "02_interactive_basin_map_shelters.png",
    "03_scenario_presets_interactive.png",
    "04_stress_test_critical_spike.png",
    "05_explain_like_farmer_trilingual.png",
    "06_whatsapp_dispatch_copy_tabs.png",
    "07_tactical_incident_download.png",
    "08_drought_spi_gamma_analysis.png",
    "09_model_audit_baseline_metrics.png",
    "10_enterprise_architecture_b2g.png",
]


def audit_critical_files():
    print("--- [1/4] Auditing Critical Files & Reports ---")
    all_ok = True
    for p in CRITICAL_ASSETS:
        rel = p.relative_to(PROJECT_ROOT)
        if not p.exists():
            print(f"  [FAIL] Missing: {rel}")
            all_ok = False
        elif p.stat().st_size == 0:
            print(f"  [FAIL] Empty file (0 bytes): {rel}")
            all_ok = False
        else:
            sz_kb = p.stat().st_size / 1024
            sz_str = f"{sz_kb / 1024:.2f} MB" if sz_kb > 1024 else f"{sz_kb:.1f} KB"
            print(f"  [PASS] {rel} ({sz_str})")
    return all_ok


def audit_screenshots():
    print("\n--- [2/4] Auditing Screenshot Suites ---")
    all_ok = True
    ss_dir = PROJECT_ROOT / "docs" / "screenshots"
    v_dir = ss_dir / "video_assets"

    print("Checking Original Presentation Screenshots:")
    for name in ORIGINAL_SCREENSHOTS:
        p = ss_dir / name
        if not p.exists() or p.stat().st_size == 0:
            print(f"  [FAIL] Missing or empty: docs/screenshots/{name}")
            all_ok = False
        else:
            print(f"  [PASS] docs/screenshots/{name} ({p.stat().st_size / 1024:.1f} KB)")

    print("\nChecking Video-Grade Storyboard Screenshots (10 Assets):")
    for name in VIDEO_SCREENSHOTS:
        p = v_dir / name
        if not p.exists() or p.stat().st_size == 0:
            print(f"  [FAIL] Missing or empty: docs/screenshots/video_assets/{name}")
            all_ok = False
        else:
            print(f"  [PASS] docs/screenshots/video_assets/{name} ({p.stat().st_size / 1024:.1f} KB)")

    zip_p = ss_dir / "JalDrishti_Video_Storyboard_Assets.zip"
    if zip_p.exists():
        try:
            with zipfile.ZipFile(zip_p, "r") as zf:
                namelist = zf.namelist()
                print(f"\n[PASS] Verified ZIP archive integrity: {len(namelist)} files bundled")
                for expected in VIDEO_SCREENSHOTS:
                    if expected not in namelist:
                        print(f"  [FAIL] ZIP missing file: {expected}")
                        all_ok = False
        except Exception as e:
            print(f"  [FAIL] Corrupt ZIP archive: {e}")
            all_ok = False
    else:
        print(f"  [FAIL] Missing ZIP archive: {zip_p}")
        all_ok = False

    return all_ok


def audit_markdown_links():
    print("\n--- [3/4] Auditing Markdown File Links & Integrity ---")
    all_ok = True
    md_files = [PROJECT_ROOT / "README.md"] + list((PROJECT_ROOT / "docs").glob("*.md"))

    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for md_file in md_files:
        rel = md_file.relative_to(PROJECT_ROOT)
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        matches = link_pattern.findall(content)

        file_links_ok = True
        for text, target in matches:
            target = target.strip()
            # Ignore anchors
            if target.startswith("#"):
                continue

            # External URL check
            if target.startswith("http://") or target.startswith("https://"):
                if target.startswith("https://https://") or target.endswith(")") or " " in target:
                    print(f"  [FAIL] Broken external link in {rel}: {target}")
                    file_links_ok = False
                    all_ok = False
            else:
                # Local relative link check
                clean_target = target.split("#")[0]
                if clean_target:
                    target_path = (md_file.parent / clean_target).resolve()
                    if not target_path.exists():
                        print(f"  [FAIL] Broken local link in {rel} -> {target}")
                        file_links_ok = False
                        all_ok = False

        if file_links_ok:
            print(f"  [PASS] {rel} ({len(matches)} links verified)")

    return all_ok


def main():
    print("=" * 80)
    print("JALDRISHTI ASSET INTEGRITY & LINK AUDIT SUITE")
    print("=" * 80)

    f1 = audit_critical_files()
    f2 = audit_screenshots()
    f3 = audit_markdown_links()

    print("\n" + "=" * 80)
    if f1 and f2 and f3:
        print("OVERALL STATUS: [100% PASS] ALL REPOSITORY ASSETS & LINKS VERIFIED CLEANLY!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("OVERALL STATUS: [WARNING] SOME AUDIT CHECKS FAILED. PLEASE REVIEW LOGS.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
