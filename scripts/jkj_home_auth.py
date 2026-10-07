"""
JKJ AI Trader
Home Morning Zerodha Authentication

Purpose:
Prepare and verify today's Zerodha session before
leaving home.

This script:
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


from modules.intraday_zerodha_session_manager import get_kite_session


def main():
    print("=" * 70)
    print("JKJ AI TRADER — HOME ZERODHA SESSION")
    print("=" * 70)
    print()

    result = get_kite_session()

    status = result.get("Status")
    kite_available = result.get("Kite") is not None

    print("Session Status :", status)
    print("Kite Available :", kite_available)
    print()

    if status in (
        "SESSION_REUSED",
        "AUTHENTICATED_AND_VERIFIED",
    ) and kite_available:

        print("JKJ ZERODHA SESSION: READY")
        print()
        print("You can now stop the Codespace and leave.")
        print("The saved session can be reused after restarting")
        print("the same Codespace at the office.")
        return 0

    print("JKJ ZERODHA SESSION: NOT READY")
    print()
    print("Reason:", result.get("Reason", "Unknown failure"))
    print()
    print("Do NOT proceed to market observation.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
