"""
JKJ AI Trader
V21.2.4 — Pre-Market Readiness

Purpose:
Prepare the NIFTY option observation environment between
09:00 and 09:15 before the market opens.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V21.1 modules
- modify main.py

Preparation sequence:
1. Confirm PRE_MARKET session
2. Establish/reuse Zerodha session
3. Load NFO instruments
4. Identify NIFTY spot
5. Identify relevant expiry
6. Prepare CE/PE candidate contracts
7. Validate contract identity
8. Return a readiness record
"""

from datetime import datetime

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)


def evaluate_pre_market_readiness(current_time=None):
    """
    Establish whether JKJ is currently inside the
    09:00-09:15 preparation window.

    This first stage intentionally performs only the
    time/session check. Zerodha and contract preparation
    will be added in subsequent stages.
    """

    session_result = get_market_session_state(current_time)

    if session_result.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Unable to evaluate market session."
        }

    session_state = session_result.get("Session State")

    if session_state != "PRE_MARKET":
        return {
            "Status": "NOT_READY",
            "Reason": "Pre-market preparation is only available during PRE_MARKET.",
            "Session State": session_state,
            "Current Time": session_result.get("Current Time"),
        }

    return {
        "Status": "READY_FOR_PRE_MARKET_PREPARATION",
        "Session State": "PRE_MARKET",
        "Current Time": session_result.get("Current Time"),
        "Preparation Window": "09:00-09:15",
        "Zerodha Session": "PENDING",
        "NFO Instruments": "PENDING",
        "NIFTY Spot": "PENDING",
        "Expiry": "PENDING",
        "CE Candidate": "PENDING",
        "PE Candidate": "PENDING",
        "Contract Identity": "PENDING",
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("JKJ AI TRADER — V21.2.4 PRE-MARKET READINESS TEST")
    print("=" * 70)

    test_time = datetime.strptime(
        "2026-09-24 09:05:00",
        "%Y-%m-%d %H:%M:%S",
    )

    result = evaluate_pre_market_readiness(
        current_time=test_time
    )

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 70)
