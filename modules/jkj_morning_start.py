"""
JKJ AI Trader
Morning Start Controller

Purpose:
Establish and validate the daily Zerodha session
before the user leaves home for the office.

This module does NOT:
- capture the 09:15 baseline
- run pre-market preparation
- start market observation
- place live orders
- create paper trades
- make BUY/SELL decisions

Expected use:
    Around 07:45 AM
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from modules.jkj_daily_zerodha_auth import authenticate_today


LIVE_ORDER = False
PAPER_TRADE = False


def run_morning_start():
    """
    Establish today's Zerodha session and report readiness.
    """

    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    print()
    print("=" * 70)
    print("JKJ AI TRADER — MORNING START")
    print("=" * 70)
    print("Time:", now.strftime("%Y-%m-%d %I:%M:%S %p"))
    print()

    result = authenticate_today()

    status = result.get("Status")
    reason = result.get("Reason")
    kite = result.get("Kite")

    print("Zerodha Status:", status)

    if reason:
        print("Reason:", reason)

    if kite is None:
        print("Kite session: NOT READY")
        print()
        print("JKJ Morning Start: NOT READY")
        print()
        print("Live Order:", LIVE_ORDER)
        print("Paper Trade:", PAPER_TRADE)
        print("=" * 70)

        return {
            "Status": "MORNING_START_NOT_READY",
            "Zerodha Status": status,
            "Reason": reason,
            "Kite Ready": False,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    print("Kite session: READY")
    print()
    print("Market preparation: WAITING FOR 09:00")
    print("09:15 baseline: WAITING")
    print("Observation: WAITING")
    print()
    print("JKJ Morning Start: READY")
    print()
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
    print("=" * 70)

    return {
        "Status": "MORNING_START_READY",
        "Zerodha Status": status,
        "Reason": reason,
        "Kite Ready": True,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


if __name__ == "__main__":
    run_morning_start()
