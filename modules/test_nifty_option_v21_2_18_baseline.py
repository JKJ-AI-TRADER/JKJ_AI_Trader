"""
Test:
    V21.2.18 - 9:15 Baseline Capture

No live order.
No paper trade.
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_18_baseline import (
    capture_915_baseline,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.18 - 9:15 BASELINE TEST")
    print("=" * 70)

    session = get_kite_session()

    if not session:
        print("ZERODHA SESSION: NOT AVAILABLE")
        return

    print("ZERODHA SESSION: SESSION_REUSED")

    kite = session["Kite"]

    print()
    print("Capturing current baseline snapshot...")
    print("(For this test, the current price is being recorded")
    print("as the baseline. We will NOT treat it as historical 9:15 data.)")
    print()

    result = capture_915_baseline(kite)

    print(f"Status: {result.get('Status')}")
    print(f"NIFTY Spot: {result.get('NIFTY Spot')}")
    print(f"Expiry: {result.get('Expiry')}")
    print(f"Universe Count: {result.get('Universe Count')}")
    print(f"Baseline Count: {result.get('Baseline Count')}")

    baseline = result.get("Baseline", [])

    print()
    print("SAMPLE BASELINE RECORDS:")
    print("-" * 70)

    for item in baseline[:10]:

        print(
            f"{item['Trading Symbol']} | "
            f"{item['Option Type']} | "
            f"Strike: {item['Strike']} | "
            f"9:15 Price: {item['9:15 Price']:.2f} | "
            f"Previous Close: "
            f"{item['Previous Close']}"
        )

    print()
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))


if __name__ == "__main__":
    main()
