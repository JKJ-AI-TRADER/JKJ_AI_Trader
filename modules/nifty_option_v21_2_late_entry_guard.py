"""
JKJ AI Trader
V21.2 — Late-Entry Protection

Purpose:
Classify whether sufficient intraday time remains for a
potential trade, without making a trading decision.

The minimum required time is configurable and will later
be determined by the V13/V14 trade-management requirements.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V21.1 modules
- modify main.py
"""

from modules.nifty_option_v21_2_time_guard import (
    evaluate_time_to_close,
)


DEFAULT_MINIMUM_TIME_REMAINING_MINUTES = 30


def evaluate_late_entry_protection(
    current_time=None,
    minimum_time_remaining_minutes=(
        DEFAULT_MINIMUM_TIME_REMAINING_MINUTES
    ),
):
    """
    Evaluate whether enough market time remains.

    This is a timing safety classification only.
    It does not authorize a trade.
    """

    if not isinstance(
        minimum_time_remaining_minutes,
        (int, float),
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Minimum time remaining must be numeric."
            ),
        }

    if minimum_time_remaining_minutes < 0:
        return {
            "Status": "REJECTED",
            "Reason": (
                "Minimum time remaining cannot be negative."
            ),
        }

    time_result = evaluate_time_to_close(
        current_time
    )

    if time_result.get("Status") == "PRE_MARKET":
        return {
            "Status": "EVALUATED",
            "Timing Classification": "PRE_MARKET",
            "Minutes Remaining": None,
            "Minimum Required Minutes": (
                minimum_time_remaining_minutes
            ),
            "Entry Timing Permission": "NOT_APPLICABLE",
        }

    if time_result.get("Status") == "MARKET_CLOSED":
        return {
            "Status": "EVALUATED",
            "Timing Classification": "MARKET_CLOSED",
            "Minutes Remaining": 0,
            "Minimum Required Minutes": (
                minimum_time_remaining_minutes
            ),
            "Entry Timing Permission": "BLOCKED",
        }

    minutes_remaining = time_result.get(
        "Minutes Remaining"
    )

    if minutes_remaining is None:
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unable to determine remaining market time."
            ),
        }

    if minutes_remaining < minimum_time_remaining_minutes:
        timing_classification = "LATE_ENTRY_WINDOW"
        entry_timing_permission = "BLOCKED"

    else:
        timing_classification = "NORMAL_ENTRY_WINDOW"
        entry_timing_permission = "TIMING_CONDITION_SATISFIED"

    return {
        "Status": "EVALUATED",
        "Timing Classification": timing_classification,
        "Minutes Remaining": minutes_remaining,
        "Minimum Required Minutes": (
            minimum_time_remaining_minutes
        ),
        "Entry Timing Permission": entry_timing_permission,
    }


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("JKJ AI Trader")
    print("V21.2 — Late-Entry Protection")
    print("=" * 60)
    print()

    result = evaluate_late_entry_protection()

    print("Status:", result.get("Status"))
    print(
        "Timing Classification:",
        result.get("Timing Classification"),
    )
    print(
        "Minutes Remaining:",
        result.get("Minutes Remaining"),
    )
    print(
        "Minimum Required Minutes:",
        result.get("Minimum Required Minutes"),
    )
    print(
        "Entry Timing Permission:",
        result.get("Entry Timing Permission"),
    )
    print()
