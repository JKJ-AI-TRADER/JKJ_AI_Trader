"""
JKJ AI Trader
V21.2.10 — Real-Market Momentum Confirmation

Purpose:
Run the existing V12.6 momentum evidence, persistence,
and confirmation logic against real-market NIFTY option observations.

This stage:
- observes real market data
- reuses existing V12.4/V12.5/V12.6 logic
- does NOT place live orders
- does NOT create paper trades
- does NOT make final entry decisions

Principle:
Observation -> Evidence -> Persistence -> Confirmation
Confirmation is NOT an entry order.
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

from modules.nifty_option_volume_oi_behavior import (
    interpret_volume_oi_behavior,
)

from modules.nifty_option_movement_relationship import (
    interpret_movement_relationship,
)

from modules.nifty_option_combined_interpretation import (
    combine_movement_interpretation,
)

from modules.nifty_option_momentum_evidence import (
    evaluate_momentum_evidence,
)

from modules.nifty_option_momentum_sequence import (
    evaluate_momentum_sequence,
)

from modules.nifty_option_momentum_confirmation import (
    evaluate_momentum_confirmation,
)


def _identity_key(observation):
    return (
        observation.get("Trading Symbol"),
        observation.get("Underlying"),
        observation.get("Expiry"),
        observation.get("Strike"),
        observation.get("Option Type"),
    )


def _build_direction_result(
    previous_observation,
    current_observation,
):
    movement = analyze_option_movement(
        previous_observation,
        current_observation,
    )

    if movement.get("Status") != "ANALYZED":
        return {
            "Status": "REJECTED",
            "Reason": "Movement analysis failed.",
            "Movement": movement,
        }

    return interpret_movement_direction(movement)


def _build_combined_interpretation(
    previous_observation,
    current_observation,
):
    movement = analyze_option_movement(
        previous_observation,
        current_observation,
    )

    if movement.get("Status") != "ANALYZED":
        return {
            "Status": "REJECTED",
            "Reason": "Movement analysis failed.",
            "Movement": movement,
        }

    direction_result = interpret_movement_direction(
        movement
    )

    if direction_result.get("Status") != "INTERPRETED":
        return direction_result

    volume_oi_result = interpret_volume_oi_behavior(
        movement
    )

    if volume_oi_result.get("Status") != "INTERPRETED":
        return volume_oi_result

    relationship_result = interpret_movement_relationship(
        direction_result
    )

    if relationship_result.get("Status") != "INTERPRETED":
        return relationship_result

    return combine_movement_interpretation(
        direction_result,
        volume_oi_result,
        relationship_result,
    )


def evaluate_real_market_momentum_confirmation(
    kite,
    contracts,
    observation_count=4,
    interval_seconds=10,
):
    """
    Capture repeated real-market observations and evaluate
    V12.6 momentum confirmation for each contract.
    """

    if not isinstance(contracts, list) or not contracts:
        return {
            "Status": "REJECTED",
            "Reason": "Contracts must be a non-empty list.",
            "Live Order": False,
            "Paper Trade": False,
        }

    if observation_count < 4:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 4 observations are required "
                "to evaluate three movement intervals."
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    observation_cycles = []

    for cycle_number in range(observation_count):

        cycle_result = capture_observation_cycle(
            kite,
            contracts,
        )

        if cycle_result.get("Status") != "OBSERVATION_CYCLE_COMPLETE":
            return {
                "Status": "REJECTED",
                "Reason": "Observation cycle failed.",
                "Cycle": cycle_number + 1,
                "Cycle Result": cycle_result,
                "Live Order": False,
                "Paper Trade": False,
            }

        observation_cycles.append(
            cycle_result["Observations"]
        )

        if cycle_number < observation_count - 1:
            time.sleep(interval_seconds)

    contract_observations = {}

    for cycle in observation_cycles:

        for observation in cycle:

            key = _identity_key(observation)

            if key not in contract_observations:
                contract_observations[key] = []

            contract_observations[key].append(
                observation
            )

    results = []

    for identity, observations in contract_observations.items():

        direction_results = []
        combined_results = []

        for index in range(1, len(observations)):

            previous_observation = observations[index - 1]
            current_observation = observations[index]

            direction_result = _build_direction_result(
                previous_observation,
                current_observation,
            )

            if direction_result.get("Status") != "INTERPRETED":
                continue

            direction_results.append(
                direction_result
            )

            combined_result = _build_combined_interpretation(
                previous_observation,
                current_observation,
            )

            if combined_result.get("Status") == "INTERPRETED":
                combined_results.append(
                    combined_result
                )

        if not direction_results:

            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": "No valid direction results.",
                "Live Order": False,
                "Paper Trade": False,
            })

            continue

        momentum_sequence = evaluate_momentum_sequence(
            direction_results
        )

        if not combined_results:

            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": "No valid combined interpretations.",
                "Momentum Sequence": momentum_sequence,
                "Live Order": False,
                "Paper Trade": False,
            })

            continue

        latest_combined = combined_results[-1]

        momentum_evidence = evaluate_momentum_evidence(
            latest_combined
        )

        momentum_confirmation = evaluate_momentum_confirmation(
            momentum_evidence,
            momentum_sequence,
        )

        results.append({
            "Trading Symbol": identity[0],
            "Underlying": identity[1],
            "Expiry": identity[2],
            "Strike": identity[3],
            "Option Type": identity[4],
            "Observation Count": len(observations),
            "Movement Intervals": len(direction_results),
            "Latest Combined Interpretation": latest_combined,
            "Momentum Evidence": momentum_evidence,
            "Momentum Sequence": momentum_sequence,
            "Momentum Confirmation": momentum_confirmation,
            "Status": momentum_confirmation.get(
                "Momentum Confirmation",
                "NOT_CONFIRMED",
            ),
            "Live Order": False,
            "Paper Trade": False,
        })

    return {
        "Status": "MOMENTUM_CONFIRMATION_COMPLETE",
        "Observation Count": observation_count,
        "Movement Intervals": observation_count - 1,
        "Contract Count": len(results),
        "Results": results,
        "Live Order": False,
        "Paper Trade": False,
    }
