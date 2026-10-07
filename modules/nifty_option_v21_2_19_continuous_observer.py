"""
JKJ AI Trader
V21.2.19 - Continuous Intraday Observation & Candidate Tracker

Purpose:
    Continuous observation of NIFTY options through the trading session.

Safety:
    - Observation only
    - NO live orders
    - NO paper trades
    - NO entry decisions
    - NO exit decisions

Design:
    Reuses the validated V21.2.18 early-surge observation engine.
    Repeated observation windows are preserved as timestamped snapshots.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

from modules.nifty_option_v21_2_18_early_surge_scanner import (
    run_early_surge_session,
)


DEFAULT_WINDOW_SECONDS = 60
DEFAULT_INTERVAL_SECONDS = 15

# Pause between completed observation windows.
DEFAULT_CYCLE_GAP_SECONDS = 5

# Maximum number of cycles unless explicitly changed.
DEFAULT_MAX_CYCLES = 1


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _print_candidate_summary(
    candidates: List[Dict[str, Any]],
) -> None:

    print()
    print("ACTIVE EARLY-SURGE CANDIDATES")
    print("-" * 70)

    if not candidates:
        print("None")
        return

    ranked = sorted(
        candidates,
        key=lambda item: (
            item.get("Window Change %", 0),
            item.get("Acceleration %", 0),
        ),
        reverse=True,
    )

    for item in ranked[:10]:

        print(
            f"{item.get('Trading Symbol')} | "
            f"{item.get('Option Type')} | "
            f"Price: {item.get('Latest Price', 0):.2f} | "
            f"Window: {item.get('Window Change %', 0):+.2f}% | "
            f"Daily: {item.get('Daily Change %', 0):+.2f}% | "
            f"Acceleration: {item.get('Acceleration %', 0):+.2f}% | "
            f"{item.get('Final Classification', 'UNKNOWN')}"
        )


def run_continuous_observer(
    kite,
    max_cycles: int = DEFAULT_MAX_CYCLES,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    cycle_gap_seconds: int = DEFAULT_CYCLE_GAP_SECONDS,
) -> Dict[str, Any]:
    """
    Run repeated V21.2.18 observation windows.

    This version intentionally does not place or simulate trades.
    """

    print()
    print("=" * 70)
    print("JKJ V21.2.19 CONTINUOUS INTRADAY OBSERVER")
    print("=" * 70)

    print(f"Started: { _timestamp() }")
    print(f"Observation Window: {window_seconds}s")
    print(f"Observation Interval: {interval_seconds}s")
    print(f"Cycle Gap: {cycle_gap_seconds}s")
    print(f"Maximum Cycles: {max_cycles}")
    print("Live Order: False")
    print("Paper Trade: False")
    print("Mode: OBSERVATION ONLY")

    history: List[Dict[str, Any]] = []

    for cycle in range(1, max_cycles + 1):

        print()
        print("=" * 70)
        print(f"V21.2.19 OBSERVATION CYCLE {cycle}/{max_cycles}")
        print(f"Timestamp: {_timestamp()}")
        print("=" * 70)

        try:

            result = run_early_surge_session(
                kite,
                window_seconds=window_seconds,
                interval_seconds=interval_seconds,
            )

        except Exception as exc:

            print()
            print(
                f"OBSERVATION ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

            history.append(
                {
                    "Timestamp": _timestamp(),
                    "Cycle": cycle,
                    "Status": "ERROR",
                    "Error": str(exc),
                    "Live Order": False,
                    "Paper Trade": False,
                }
            )

            if cycle < max_cycles:
                time.sleep(cycle_gap_seconds)

            continue

        candidates = result.get("Candidates", [])

        snapshot = {
            "Timestamp": _timestamp(),
            "Cycle": cycle,
            "Status": result.get("Status"),
            "NIFTY Spot": result.get("NIFTY Spot"),
            "Expiry": result.get("Expiry"),
            "Universe Count": result.get("Universe Count", 0),
            "Candidate Count": len(candidates),
            "Candidates": candidates,
            "CE Candidate Count": len(
                result.get("CE Upward Candidates", [])
            ),
            "PE Candidate Count": len(
                result.get("PE Upward Candidates", [])
            ),
            "CE Multi-Strike Confirmation": result.get(
                "CE Multi-Strike Confirmation",
                False,
            ),
            "PE Multi-Strike Confirmation": result.get(
                "PE Multi-Strike Confirmation",
                False,
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

        history.append(snapshot)

        print()
        print("V21.2.19 CYCLE SUMMARY")
        print("-" * 70)
        print(f"NIFTY Spot: {snapshot['NIFTY Spot']}")
        print(f"Candidates: {snapshot['Candidate Count']}")
        print(
            f"CE Multi-Strike: "
            f"{snapshot['CE Multi-Strike Confirmation']}"
        )
        print(
            f"PE Multi-Strike: "
            f"{snapshot['PE Multi-Strike Confirmation']}"
        )

        _print_candidate_summary(candidates)

        if cycle < max_cycles:

            print()
            print(
                f"Waiting {cycle_gap_seconds}s "
                "before next observation cycle..."
            )

            time.sleep(cycle_gap_seconds)

    print()
    print("=" * 70)
    print("V21.2.19 CONTINUOUS OBSERVER COMPLETE")
    print("=" * 70)
    print(f"Cycles Completed: {len(history)}")
    print("Live Order: False")
    print("Paper Trade: False")

    total_candidate_snapshots = sum(
        item.get("Candidate Count", 0)
        for item in history
        if isinstance(item, dict)
    )

    print(
        f"Total Candidate Snapshots: "
        f"{total_candidate_snapshots}"
    )

    return {
        "Status": "CONTINUOUS_OBSERVER_COMPLETE",
        "Cycles Completed": len(history),
        "History": history,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print(
        "This module requires an authenticated Kite session."
    )
    print(
        "Use run_continuous_observer(kite, ...) "
        "from the JKJ runtime."
    )
