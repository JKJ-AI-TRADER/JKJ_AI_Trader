"""
JKJ AI Trader
V21.2.18.2 Historical Observation Replay

Purpose:
Validate V21.2.18.2 against the existing historical
nifty_option_observations.csv.

IMPORTANT:
The CSV does not contain a genuine 9:15 baseline for these
records. Therefore this script does NOT fabricate 9:15 movement.

This is an observation-history validation only.

No:
- Zerodha connection
- live order
- paper trade
- BUY/SELL decision
"""

import csv
import os
import sys
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.nifty_option_early_surge_analyzer import (
    analyze_observation_history,
)
from modules.nifty_option_early_surge_candidate_discovery import (
    discover_early_surge_candidates,
)


CSV_FILE = os.path.join(
    PROJECT_ROOT,
    "nifty_option_observations.csv",
)


def load_history():
    histories = defaultdict(list)

    with open(
        CSV_FILE,
        newline="",
        encoding="utf-8",
    ) as handle:

        reader = csv.DictReader(handle)

        for row_number, row in enumerate(reader, start=1):

            symbol = row.get("Trading Symbol")

            if not symbol:
                continue

            current_price = row.get("Current Price")

            try:
                current_price = float(current_price)
            except (TypeError, ValueError):
                continue

            histories[symbol].append(
                {
                    "Status": "RECORDED",
                    "Trading Symbol": symbol,
                    "Observation Number": len(
                        histories[symbol]
                    ) + 1,
                    "Timestamp": row.get("Timestamp"),
                    "Current Price": current_price,
                    "Underlying": row.get("Underlying"),
                    "Expiry": row.get("Expiry"),
                    "Strike": row.get("Strike"),
                    "Option Type": row.get("Option Type"),
                    "Volume": row.get("Volume"),
                    "Open Interest": row.get("Open Interest"),
                    "NIFTY Spot Price": row.get(
                        "NIFTY Spot Price"
                    ),
                }
            )

    return dict(histories)


def make_candidate(symbol, history):
    """
    Build a discovery record without inventing 9:15 movement.

    Movement Since 9:15 remains None because the CSV has no
    genuine 9:15 baseline.
    """

    latest = history[-1]

    option_type = latest.get("Option Type") or ""

    try:
        strike = float(latest.get("Strike"))
    except (TypeError, ValueError):
        strike = 0.0

    return {
        "Trading Symbol": symbol,
        "Option Type": option_type,
        "Strike": strike,
        "Expiry": latest.get("Expiry"),
        "Previous Close": None,
        "9:15 Price": None,
        "Initial Price": history[0]["Current Price"],
        "Latest Price": latest["Current Price"],
        "Movement Since 9:15 %": None,
        "9:15 Movement Level": "BASELINE_UNAVAILABLE",
        "Daily Change %": 0.0,
        "Window Change %": 0.0,
        "Acceleration %": 0.0,
        "Initial Classification": "HISTORICAL_REPLAY",
        "Final Classification": "HISTORICAL_REPLAY",
        "Reversal Up": False,
        "Upward Acceleration": False,
        "Early Surge Candidate": True,
    }


def make_scanner_result(histories):
    candidates = []

    for symbol, history in histories.items():
        candidates.append(
            make_candidate(symbol, history)
        )

    return {
        "Status": "SCAN_COMPLETE",
        "NIFTY Spot": None,
        "Expiry": None,
        "Universe Count": len(candidates),
        "Results": candidates,
        "Candidates": candidates,
        "Live Order": False,
        "Paper Trade": False,
    }


def make_observation_result(histories):
    observations_by_contract = {}

    for symbol, history in histories.items():
        observations_by_contract[
            ("NIFTY", symbol)
        ] = history

    return {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",
        "Observation Count": max(
            len(history)
            for history in histories.values()
        ),
        "Movement Intervals": 0,
        "Interval Seconds": None,
        "Contract Count": len(histories),
        "Observations By Contract": (
            observations_by_contract
        ),
        "Latest Observations": {},
        "Live Order": False,
        "Paper Trade": False,
    }


def print_analyzer_summary(symbol, history):
    analysis = analyze_observation_history(
        history
    )

    print()
    print("-" * 72)
    print(symbol)
    print("-" * 72)

    print(
        "Observation Count:",
        analysis.get("Observation Count"),
    )

    print(
        "Overall State:",
        analysis.get("Overall State"),
    )

    print(
        "Latest State:",
        analysis.get("Latest State"),
    )

    print(
        "Peak Price:",
        analysis.get("Peak Price"),
    )

    print(
        "Peak Observation:",
        analysis.get("Peak Observation Number"),
    )

    print(
        "Persistent Acceleration:",
        analysis.get("Persistent Acceleration"),
    )

    print(
        "Positive Movement Count:",
        analysis.get("Positive Movement Count"),
    )

    print(
        "Accelerating Count:",
        analysis.get("Accelerating Observation Count"),
    )

    print(
        "Decelerating Count:",
        analysis.get("Decelerating Observation Count"),
    )

    observations = analysis.get(
        "Observations",
        [],
    )

    print()
    print(
        "Observation States:"
    )

    for observation in observations:

        print(
            f"{observation.get('Observation Number'):>3} | "
            f"{observation.get('Timestamp')} | "
            f"Price={observation.get('Price')} | "
            f"Move={observation.get('Movement %')} | "
            f"Velocity={observation.get('Velocity %/sec')} | "
            f"Acceleration={observation.get('Acceleration %/sec²')} | "
            f"State={observation.get('State')} | "
            f"Drawdown={observation.get('Drawdown From Peak %')}"
        )

    return analysis


def main():

    print()
    print("=" * 72)
    print("JKJ V21.2.18.2 HISTORICAL OBSERVATION REPLAY")
    print("=" * 72)

    print()
    print("Source:", CSV_FILE)

    histories = load_history()

    print(
        "Historical Symbols:",
        len(histories),
    )

    total_rows = sum(
        len(history)
        for history in histories.values()
    )

    print(
        "Historical Observations:",
        total_rows,
    )

    print()
    print(
        "NOTE: Genuine 9:15 baseline is unavailable."
    )
    print(
        "9:15 movement will NOT be fabricated."
    )

    # --------------------------------------------------------------
    # Direct analyzer replay
    # --------------------------------------------------------------

    analyses = {}

    for symbol, history in histories.items():

        if len(history) < 4:
            print()
            print(
                symbol,
                "SKIPPED - fewer than 4 observations",
            )
            continue

        analyses[symbol] = print_analyzer_summary(
            symbol,
            history,
        )

    # --------------------------------------------------------------
    # V21.2.18.2 integration replay
    # --------------------------------------------------------------

    scanner_result = make_scanner_result(
        histories
    )

    observation_result = make_observation_result(
        histories
    )

    discovery = discover_early_surge_candidates(
        scanner_result,
        observation_result,
    )

    print()
    print("=" * 72)
    print("V21.2.18.2 DISCOVERY INTEGRATION")
    print("=" * 72)

    print()
    print(
        "Status:",
        discovery.get("Status"),
    )

    print(
        "Discovery Candidates:",
        discovery.get("Discovery Candidate Count"),
    )

    for candidate in discovery.get(
        "Candidates",
        [],
    ):

        print()
        print(
            candidate.get("Trading Symbol")
        )

        print(
            "  State:",
            candidate.get("State"),
        )

        print(
            "  Observation Status:",
            candidate.get("Observation Status"),
        )

        print(
            "  Observation Count:",
            candidate.get("Observation Count"),
        )

        print(
            "  Analyzer Overall State:",
            candidate.get(
                "Analyzer Overall State"
            ),
        )

        print(
            "  Analyzer Latest State:",
            candidate.get(
                "Analyzer Latest State"
            ),
        )

        print(
            "  Persistent Acceleration:",
            candidate.get(
                "Persistent Acceleration"
            ),
        )

        print(
            "  Reason:",
            candidate.get("Reason"),
        )

        print(
            "  Live Order:",
            candidate.get("Live Order"),
        )

        print(
            "  Paper Trade:",
            candidate.get("Paper Trade"),
        )

    print()
    print("=" * 72)
    print("HISTORICAL REPLAY COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
