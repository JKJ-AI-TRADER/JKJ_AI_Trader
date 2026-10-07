"""
JKJ AI Trader
Office Morning Market Startup

Purpose:
Resume JKJ after restarting the Codespace at the office.

This script:
- reuses the saved daily Zerodha session
- verifies NIFTY and NFO
- respects market timing
- does not place orders
- does not enable live trading
- does not enable paper trading
- does not make trading decisions
"""

import os
import sys


# Add the JKJ project root to Python's import path.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from modules.jkj_morning_startup import run_morning_startup


def main():
    print("=" * 70)
    print("JKJ AI TRADER — OFFICE MARKET STARTUP")
    print("=" * 70)
    print()

    result = run_morning_startup()

    print("Status:", result.get("Status"))
    print("Current Time:", result.get("Current Time"))
    print("Zerodha Session:", result.get("Zerodha Session"))
    print("NIFTY:", result.get("NIFTY"))
    print("NFO:", result.get("NFO"))
    print("Next Stage:", result.get("Next Stage"))
    print("Live Trading:", result.get("Live Trading"))
    print("Paper Trading:", result.get("Paper Trading"))
    print(
        "Order Placement Permitted:",
        result.get("Order Placement Permitted")
    )
    print()

    if result.get("Zerodha Session") != "SESSION_READY":
        print("JKJ OFFICE STARTUP: NOT READY")
        print("Do NOT proceed to market observation.")
        return 1

    print("JKJ OFFICE STARTUP: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
