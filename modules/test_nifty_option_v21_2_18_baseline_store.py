"""
JKJ AI TRADER
V21.2.18 - Baseline Store Test

No live order.
No paper trade.
"""

from modules.nifty_option_v21_2_18_baseline_store import (
    save_baseline,
    load_today_baseline,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.18 - 9:15 BASELINE STORE TEST")
    print("=" * 70)

    # Test object only.
    test_result = {
        "Status": "BASELINE_CAPTURE_COMPLETE",
        "Baseline Time": "09:15",
        "Captured At": "TEST",
        "NIFTY Spot": 23114.0,
        "Expiry": "2026-09-29",
        "Universe Count": 42,
        "Baseline Count": 42,
        "Baseline": [],
        "Live Order": False,
        "Paper Trade": False,
    }

    saved = save_baseline(test_result)

    print()
    print("SAVE RESULT:")
    print(saved)

    loaded = load_today_baseline()

    print()
    print("LOAD RESULT:")

    if loaded:
        print("Today's baseline: AVAILABLE")
        print(
            "Baseline Status:",
            loaded.get("Status"),
        )
        print(
            "Baseline Time:",
            loaded.get("Baseline Time"),
        )
        print(
            "NIFTY Spot:",
            loaded.get("NIFTY Spot"),
        )
    else:
        print("Today's baseline: NOT AVAILABLE")

    print()
    print("Live Order: False")
    print("Paper Trade: False")


if __name__ == "__main__":
    main()
