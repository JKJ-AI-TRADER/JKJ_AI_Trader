"""
JKJ AI Trader
V21.2.4 — NFO Preparation

Purpose:
Reuse the existing secure Zerodha session and load the
NFO instrument master for pre-market preparation.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- select final trading opportunities
- modify V12.1-V21.1 modules
- modify main.py
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)


def prepare_nfo_instruments():
    """
    Establish/reuse the existing Zerodha session and load
    the NFO instrument master.

    Returns a preparation record only.
    """

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return {
            "Status": "FAILED",
            "Reason": "Unexpected Zerodha session result.",
            "Live Order": False,
            "Paper Trade": False,
        }

    session_status = session_result.get("Status")

    if session_status not in (
        "SESSION_REUSED",
        "SESSION_CREATED",
        "AUTHENTICATED",
    ):
        return {
            "Status": "FAILED",
            "Reason": session_result.get(
                "Reason",
                "Zerodha session was not established.",
            ),
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    kite = session_result.get("Kite")

    if kite is None:
        return {
            "Status": "FAILED",
            "Reason": "Kite session object is missing.",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    try:
        instruments = kite.instruments("NFO")

    except Exception as error:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to load NFO instruments: {error}",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(instruments, list):
        return {
            "Status": "FAILED",
            "Reason": "NFO instrument response is not a list.",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    if not instruments:
        return {
            "Status": "FAILED",
            "Reason": "NFO instrument list is empty.",
            "Session Status": session_status,
            "NFO Instruments": 0,
            "Live Order": False,
            "Paper Trade": False,
        }

    return {
        "Status": "NFO_READY",
        "Session Status": session_status,
        "NFO Instruments": len(instruments),
        "NFO Instrument Data": instruments,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("JKJ AI TRADER — V21.2.4 NFO PREPARATION TEST")
    print("=" * 70)

    result = prepare_nfo_instruments()

    for key, value in result.items():

        if key == "NFO Instrument Data":
            print(
                f"{key}: "
                f"{len(value) if isinstance(value, list) else value}"
            )
        else:
            print(f"{key}: {value}")

    print("=" * 70)
