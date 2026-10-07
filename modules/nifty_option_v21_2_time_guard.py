"""
JKJ AI Trader
V21.2 — Time-to-Close Guard

Purpose:
Calculate the remaining NIFTY intraday trading time and
provide a safe foundation for late-entry protection.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- set a final entry cutoff
- modify V12.1-V21.1 modules
- modify main.py
"""

from datetime import datetime, time


MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def evaluate_time_to_close(current_time=None):
    """
    Calculate the time remaining until the 15:30 market close.

    This stage reports timing information only.
    It does not decide whether a trade should be entered.
    """

    if current_time is None:
        current_time = datetime.now()

    if not isinstance(current_time, datetime):
        return {
            "Status": "REJECTED",
            "Reason": "current_time must be a datetime.",
        }

    current_clock = current_time.time()

    if current_clock < MARKET_OPEN:
        return {
            "Status": "PRE_MARKET",
            "Current Time": current_time.isoformat(),
            "Minutes Remaining": None,
            "Seconds Remaining": None,
            "Entry Timing Status": "NOT_IN_MARKET",
        }

    if current_clock >= MARKET_CLOSE:
        return {
            "Status": "MARKET_CLOSED",
            "Current Time": current_time.isoformat(),
            "Minutes Remaining": 0,
            "Seconds Remaining": 0,
            "Entry Timing Status": "CLOSED",
        }

    close_datetime = current_time.replace(
        hour=MARKET_CLOSE.hour,
        minute=MARKET_CLOSE.minute,
        second=0,
        microsecond=0,
    )

    remaining_seconds = int(
        (close_datetime - current_time).total_seconds()
    )

    return {
        "Status": "EVALUATED",
        "Current Time": current_time.isoformat(),
        "Market Close": close_datetime.isoformat(),
        "Minutes Remaining": remaining_seconds // 60,
        "Seconds Remaining": remaining_seconds,
        "Entry Timing Status": "WITHIN_MARKET_SESSION",
    }


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("JKJ AI Trader")
    print("V21.2 — Time-to-Close Guard")
    print("=" * 60)
    print()

    result = evaluate_time_to_close()

    print("Status:", result.get("Status"))
    print("Current Time:", result.get("Current Time"))
    print("Minutes Remaining:", result.get("Minutes Remaining"))
    print("Seconds Remaining:", result.get("Seconds Remaining"))
    print("Entry Timing Status:",
          result.get("Entry Timing Status"))
    print()
