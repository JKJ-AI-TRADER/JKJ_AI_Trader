"""
JKJ AI Trader
V21.2 — Market Session Controller

Purpose:
Define the JKJ intraday operating windows.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- select trading opportunities
- modify V12.1-V21.1 modules
- modify main.py

Session design:
09:00       PRE_MARKET
09:15-15:30 MARKET_SESSION
15:30       MARKET_CLOSED
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo


PRE_MARKET_START = time(9, 0)
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def get_market_session_state(current_time=None):
    """
    Return the current JKJ market-session state.

    Parameters
    ----------
    current_time : datetime, optional
        Local datetime used for evaluation.
        If omitted, the system's current local datetime is used.

    Returns
    -------
    dict
        Session state and timing information.
    """

    if current_time is None:
        current_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    if not isinstance(current_time, datetime):
        return {
            "Status": "REJECTED",
            "Reason": "current_time must be a datetime.",
        }

    current_clock = current_time.time()

    if current_clock < PRE_MARKET_START:
        state = "BEFORE_PRE_MARKET"

    elif current_clock < MARKET_OPEN:
        state = "PRE_MARKET"

    elif current_clock < MARKET_CLOSE:
        state = "MARKET_SESSION"

    else:
        state = "MARKET_CLOSED"

    return {
        "Status": "EVALUATED",
        "Session State": state,
        "Current Time": current_time.isoformat(),
        "Pre-Market Start": PRE_MARKET_START.isoformat(),
        "Market Open": MARKET_OPEN.isoformat(),
        "Market Close": MARKET_CLOSE.isoformat(),
    }


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("JKJ AI Trader")
    print("V21.2 — Market Session Controller")
    print("=" * 60)
    print()

    result = get_market_session_state()

    print("Status:", result.get("Status"))
    print("Session State:", result.get("Session State"))
    print("Current Time:", result.get("Current Time"))
    print("Pre-Market Start:", result.get("Pre-Market Start"))
    print("Market Open:", result.get("Market Open"))
    print("Market Close:", result.get("Market Close"))
    print()
