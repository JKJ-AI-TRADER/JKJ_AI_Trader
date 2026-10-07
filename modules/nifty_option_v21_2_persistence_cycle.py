"""
JKJ AI Trader
V21.2.8 — Observation Persistence Cycle

Purpose:
Capture two real-market observation cycles for the same
validated NIFTY option contracts and compare consecutive
observations using the existing V12.4 movement and V12.5
direction engines.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V21.1 modules
- modify main.py
"""

import time

from modules.nifty_option_v21_2_observation_cycle import (
    capture_observation_cycle,
)

from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)

from modules.nifty_option_movement_direction import (
    interpret_movement_direction,
)


def _build_identity(observation):
    """
    Build the identity used to match the same contract
    between observation cycles.
    """

    return (
        observation.get("Trading Symbol"),
        observation.get("Instrument Token"),
        observation.get("Expiry"),
        observation.get("Strike"),
        observation.get("Option Type"),
    )


def evaluate_persistence_cycle(
    kite,
    contracts,
    interval_seconds=10,
):
    """
    Capture two observation cycles and compare the same
    contracts between the two cycles.
    """

    if kite is None:
        return {
            "Status": "REJECTED",
            "Reason": "Kite session is required.",
        }

    if not isinstance(contracts, list) or not contracts:
        return {
            "Status": "REJECTED",
            "Reason": "Observation contracts are required.",
        }

    if not isinstance(
        interval_seconds,
        (int, float),
    ) or interval_seconds < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Interval must be a non-negative number.",
        }

    # --------------------------------------------------
    # CYCLE 1
    # --------------------------------------------------

    first_cycle = capture_observation_cycle(
        kite,
        contracts,
    )

    if first_cycle.get("Status") != "OBSERVATION_CYCLE_COMPLETE":
        return {
            "Status": "REJECTED",
            "Stage": "FIRST_CYCLE",
            "Reason": first_cycle.get(
                "Reason",
                "First observation cycle failed.",
            ),
        }

    if interval_seconds > 0:
        time.sleep(interval_seconds)

    # --------------------------------------------------
    # CYCLE 2
    # --------------------------------------------------

    second_cycle = capture_observation_cycle(
        kite,
        contracts,
    )

    if second_cycle.get("Status") != "OBSERVATION_CYCLE_COMPLETE":
        return {
            "Status": "REJECTED",
            "Stage": "SECOND_CYCLE",
            "Reason": second_cycle.get(
                "Reason",
                "Second observation cycle failed.",
            ),
        }

    first_observations = first_cycle.get(
        "Observations",
        []
    )

    second_observations = second_cycle.get(
        "Observations",
        []
    )

    if len(first_observations) != len(
        second_observations
    ):
        return {
            "Status": "REJECTED",
            "Stage": "IDENTITY",
            "Reason": "Observation cycle counts do not match.",
        }

    # --------------------------------------------------
    # MATCH SAME CONTRACTS
    # --------------------------------------------------

    first_by_identity = {
        _build_identity(item): item
        for item in first_observations
    }

    second_by_identity = {
        _build_identity(item): item
        for item in second_observations
    }

    if set(first_by_identity.keys()) != set(
        second_by_identity.keys()
    ):
        return {
            "Status": "REJECTED",
            "Stage": "IDENTITY",
            "Reason": (
                "Contract identities changed between "
                "observation cycles."
            ),
        }

    # --------------------------------------------------
    # V12.4 + V12.5
    # --------------------------------------------------

    movement_results = []
    direction_results = []

    for identity in first_by_identity:

        previous_observation = first_by_identity[
            identity
        ]

        current_observation = second_by_identity[
            identity
        ]

        movement = analyze_option_movement(
            previous_observation,
            current_observation,
        )

        if movement.get("Status") != "ANALYZED":
            return {
                "Status": "REJECTED",
                "Stage": "V12.4_MOVEMENT",
                "Reason": movement.get(
                    "Reason",
                    "Movement analysis failed.",
                ),
                "Trading Symbol": identity[0],
            }

        direction = interpret_movement_direction(
            movement
        )

        if direction.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Stage": "V12.5_DIRECTION",
                "Reason": direction.get(
                    "Reason",
                    "Direction interpretation failed.",
                ),
                "Trading Symbol": identity[0],
            }

        movement_results.append(
            movement
        )

        direction_results.append(
            direction
        )

    return {
        "Status": "PERSISTENCE_CYCLE_COMPLETE",
        "First Cycle": first_cycle,
        "Second Cycle": second_cycle,
        "Movement Results": movement_results,
        "Direction Results": direction_results,
        "Comparison Count": len(
            movement_results
        ),
        "Live Order": False,
        "Paper Trade": False,
    }
