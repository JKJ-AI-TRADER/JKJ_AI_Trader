"""
JKJ AI Trader
V21.2.9 — Multi-Cycle Persistence Sequence

Purpose:
Capture four observations of the same prepared NIFTY
option contracts and evaluate three consecutive movement
intervals using V12.4 and V12.5, followed by V12.6
momentum-sequence evaluation.

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

from modules.nifty_option_momentum_sequence import (
    evaluate_momentum_sequence,
)


def _build_identity(observation):
    return (
        observation.get("Trading Symbol"),
        observation.get("Instrument Token"),
        observation.get("Expiry"),
        observation.get("Strike"),
        observation.get("Option Type"),
    )


def evaluate_persistence_sequence(
    kite,
    contracts,
    observation_count=4,
    interval_seconds=10,
):
    """
    Capture multiple observation cycles and evaluate
    movement, direction and persistence.
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

    if not isinstance(observation_count, int):
        return {
            "Status": "REJECTED",
            "Reason": "Observation count must be an integer.",
        }

    if observation_count < 4:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 4 observations are required "
                "for three movement intervals."
            ),
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
    # OBSERVATION SEQUENCES
    # --------------------------------------------------

    observation_cycles = []

    for cycle_index in range(observation_count):

        if cycle_index > 0 and interval_seconds > 0:
            time.sleep(interval_seconds)

        cycle = capture_observation_cycle(
            kite,
            contracts,
        )

        if cycle.get(
            "Status"
        ) != "OBSERVATION_CYCLE_COMPLETE":
            return {
                "Status": "REJECTED",
                "Stage": "OBSERVATION",
                "Cycle": cycle_index + 1,
                "Reason": cycle.get(
                    "Reason",
                    "Observation cycle failed.",
                ),
            }

        observation_cycles.append(
            cycle
        )

    # --------------------------------------------------
    # BUILD IDENTITY MAPS
    # --------------------------------------------------

    cycle_maps = []

    for cycle in observation_cycles:

        observations = cycle.get(
            "Observations",
            []
        )

        identity_map = {
            _build_identity(observation): observation
            for observation in observations
        }

        cycle_maps.append(
            identity_map
        )

    base_identities = set(
        cycle_maps[0].keys()
    )

    for identity_map in cycle_maps[1:]:

        if set(identity_map.keys()) != base_identities:
            return {
                "Status": "REJECTED",
                "Stage": "IDENTITY",
                "Reason": (
                    "Contract identities changed during "
                    "the observation sequence."
                ),
            }

    # --------------------------------------------------
    # V12.4 + V12.5
    # --------------------------------------------------

    movement_results_by_contract = {}
    direction_results_by_contract = {}

    for identity in base_identities:

        movement_results = []
        direction_results = []

        for index in range(
            1,
            len(cycle_maps),
        ):

            previous_observation = cycle_maps[
                index - 1
            ][identity]

            current_observation = cycle_maps[
                index
            ][identity]

            movement = analyze_option_movement(
                previous_observation,
                current_observation,
            )

            if movement.get(
                "Status"
            ) != "ANALYZED":
                return {
                    "Status": "REJECTED",
                    "Stage": "V12.4_MOVEMENT",
                    "Trading Symbol": identity[0],
                    "Reason": movement.get(
                        "Reason",
                        "Movement analysis failed.",
                    ),
                }

            direction = interpret_movement_direction(
                movement
            )

            if direction.get(
                "Status"
            ) != "INTERPRETED":
                return {
                    "Status": "REJECTED",
                    "Stage": "V12.5_DIRECTION",
                    "Trading Symbol": identity[0],
                    "Reason": direction.get(
                        "Reason",
                        "Direction interpretation failed.",
                    ),
                }

            movement_results.append(
                movement
            )

            direction_results.append(
                direction
            )

        movement_results_by_contract[
            identity
        ] = movement_results

        direction_results_by_contract[
            identity
        ] = direction_results

    # --------------------------------------------------
    # V12.6 — PERSISTENCE
    # --------------------------------------------------

    persistence_results = {}

    for identity, direction_results in (
        direction_results_by_contract.items()
    ):

        persistence = evaluate_momentum_sequence(
            direction_results
        )

        persistence_results[
            identity
        ] = persistence

    return {
        "Status": "PERSISTENCE_SEQUENCE_COMPLETE",
        "Observation Count": observation_count,
        "Movement Intervals": observation_count - 1,
        "Observation Cycles": observation_cycles,
        "Movement Results": movement_results_by_contract,
        "Direction Results": direction_results_by_contract,
        "Persistence Results": persistence_results,
        "Live Order": False,
        "Paper Trade": False,
    }
