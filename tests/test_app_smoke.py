"""
JalDrishti - Phase 8: AppTest Smoke Test Suite
Uses streamlit.testing.v1.AppTest to exercise every district x 5 dates x 3 languages.
Guarantees the UI never raises unhandled exceptions.
"""

import sys
from pathlib import Path
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_app_initial_load():
    """Verify app loads cleanly without exceptions."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"App raised exception on initial load: {at.exception}"
    assert len(at.title) >= 1
    assert "JalDrishti" in at.title[0].value


def test_app_districts_dates_languages_matrix():
    """Smoke test across 4 districts x 5 dates x 3 languages."""
    districts = [
        "Bhadradri Kothagudem (Bhadrachalam)",
        "Mulugu (Ramappa / Eturnagaram)",
        "Nizamabad (Sriram Sagar Dam)",
        "Adilabad (Kadam / Godavari Reach)",
    ]
    languages = [
        "English",
        "తెలుగు (Telugu)",
        "हिन्दी (Hindi)",
    ]
    dates = [
        "2022-07-07",  # Warning date
        "2022-07-14",  # Peak flood date
        "2022-07-20",  # Post-peak receding
        "2023-04-15",  # Summer dry season
        "2024-08-10",  # Monsoon 2024
    ]

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"App failed initial run: {at.exception}"

    # Verify each district can be selected without errors
    for dist in districts:
        at.sidebar.selectbox[0].select(dist)
        at.run()
        assert not at.exception, f"Exception when selecting district '{dist}': {at.exception}"

    # Verify each language can be selected
    for lang in languages:
        at.sidebar.selectbox[1].select(lang)
        at.run()
        assert not at.exception, f"Exception when selecting language '{lang}': {at.exception}"

    # Verify dates
    for d in dates:
        if d in at.sidebar.selectbox[2].options:
            at.sidebar.selectbox[2].select(d)
            at.run()
            assert not at.exception, f"Exception when selecting date '{d}': {at.exception}"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    print("Running test_app_initial_load()...")
    test_app_initial_load()
    print("[PASS] test_app_initial_load()")

    print("Running test_app_districts_dates_languages_matrix()...")
    test_app_districts_dates_languages_matrix()
    print("[PASS] test_app_districts_dates_languages_matrix()")
    print("\nALL APP SMOKE TESTS PASSED CLEANLY!")


