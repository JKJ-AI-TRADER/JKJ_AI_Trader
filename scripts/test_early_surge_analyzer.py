import os
import sys

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


def run_test(name, prices):
    observations = []

    for index, price in enumerate(prices):
        observations.append(
            {
                "Current Price": price,
                "Observation Timestamp": (
                    f"2026-09-28T10:{index:02d}:00"
                ),
            }
        )

    result = analyze_observation_history(
        observations
    )

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    print(
        "Status:",
        result.get("Status"),
    )

    print(
        "Overall State:",
        result.get("Overall State"),
    )

    print(
        "Peak Price:",
        result.get("Peak Price"),
    )

    print(
        "Persistent Acceleration:",
        result.get("Persistent Acceleration"),
    )

    for observation in result.get(
        "Observations",
        [],
    ):
        print(
            f"Obs {observation['Observation Number']} | "
            f"Price {observation['Price']:.2f} | "
            f"Movement {observation['Movement %']} | "
            f"Velocity {observation['Velocity %/sec']} | "
            f"Acceleration {observation['Acceleration %/sec²']} | "
            f"Drawdown {observation['Drawdown From Peak %']} | "
            f"State {observation['State']}"
        )


# ------------------------------------------------------------
# TEST 1 — Accelerating rise
# ------------------------------------------------------------

run_test(
    "TEST 1 — ACCELERATING RISE",
    [20, 21, 23, 27, 32],
)


# ------------------------------------------------------------
# TEST 2 — Rise then fall
# ------------------------------------------------------------

run_test(
    "TEST 2 — RISE → PEAK → FALL",
    [20, 25, 32, 40, 38, 34, 28],
)


# ------------------------------------------------------------
# TEST 3 — Rise then weakening
# ------------------------------------------------------------

run_test(
    "TEST 3 — RISE → WEAKENING",
    [20, 25, 30, 34, 35, 35.5],
)


# ------------------------------------------------------------
# TEST 4 — Small movement without acceleration
# ------------------------------------------------------------

run_test(
    "TEST 4 — SMALL / STEADY MOVEMENT",
    [20, 20.2, 20.4, 20.6, 20.8],
)
