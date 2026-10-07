"""
JKJ AI Trader
V21.2.15 — Unified Observation → Momentum Bridge

Purpose:
    Process the ONE observation session captured by V21.2.15
    through the existing V12.4, V12.5 and V12.6 architecture.

Important:
    This module DOES NOT capture new market observations.

Architecture:

    V21.2.15 Unified Observation
              ↓
        V12.4 Movement
              ↓
        V12.5 Interpretation
              ↓
        V12.6 Momentum
              ↓
        V21.2.10-compatible result

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.nifty_option_v21_2_momentum_confirmation import (
    _identity_key,
    _build_direction_result,
    _build_combined_interpretation,
)

from modules.nifty_option_momentum_sequence import (
    evaluate_momentum_sequence,
)

from modules.nifty_option_momentum_evidence import (
    evaluate_momentum_evidence,
)

from modules.nifty_option_momentum_confirmation import (
    evaluate_momentum_confirmation,
)


def evaluate_unified_observation_momentum(
    unified_observation_result,
):
    """
    Evaluate an already-captured V21.2.15 observation session.

    No new Zerodha observations are captured.
    """

    if not isinstance(unified_observation_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unified observation result must "
                "be a dictionary"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if unified_observation_result.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unified observation session is "
                "not complete"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    observation_count = unified_observation_result.get(
        "Observation Count"
    )

    if not isinstance(observation_count, int):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Observation Count must be an integer"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if observation_count < 4:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 4 observations are required "
                "for V12.6 momentum evaluation"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    observations_by_contract = (
        unified_observation_result.get(
            "Observations By Contract"
        )
    )

    if not isinstance(
        observations_by_contract,
        dict,
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Observations By Contract must "
                "be a dictionary"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    results = []

    # ---------------------------------------------------------
    # Process each contract using the EXISTING V21.2.10 logic
    # ---------------------------------------------------------

    for identity, observations in (
        observations_by_contract.items()
    ):

        if not isinstance(observations, list):
            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": (
                    "Contract observation history "
                    "is not a list"
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        if len(observations) < 4:
            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": (
                    "Contract has fewer than "
                    "4 observations"
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        direction_results = []
        combined_results = []

        # -----------------------------------------------------
        # V12.4 → V12.5
        # -----------------------------------------------------

        for index in range(1, len(observations)):

            previous_observation = observations[
                index - 1
            ]

            current_observation = observations[
                index
            ]

            direction_result = _build_direction_result(
                previous_observation,
                current_observation,
            )

            if direction_result.get(
                "Status"
            ) != "INTERPRETED":
                continue

            direction_results.append(
                direction_result
            )

            combined_result = (
                _build_combined_interpretation(
                    previous_observation,
                    current_observation,
                )
            )

            if combined_result.get(
                "Status"
            ) == "INTERPRETED":

                combined_results.append(
                    combined_result
                )

        # -----------------------------------------------------
        # V12.6 Momentum
        # -----------------------------------------------------

        if not direction_results:

            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": (
                    "No valid direction results"
                ),
                "Live Order": False,
                "Paper Trade": False,
            })

            continue

        momentum_sequence = (
            evaluate_momentum_sequence(
                direction_results
            )
        )

        if not combined_results:

            results.append({
                "Trading Symbol": identity[0],
                "Option Type": identity[4],
                "Status": "NOT_EVALUATED",
                "Reason": (
                    "No valid combined interpretations"
                ),
                "Momentum Sequence": (
                    momentum_sequence
                ),
                "Live Order": False,
                "Paper Trade": False,
            })

            continue

        latest_combined = combined_results[-1]

        momentum_evidence = (
            evaluate_momentum_evidence(
                latest_combined
            )
        )

        momentum_confirmation = (
            evaluate_momentum_confirmation(
                momentum_evidence,
                momentum_sequence,
            )
        )

        results.append({
            "Trading Symbol": identity[0],
            "Underlying": identity[1],
            "Expiry": identity[2],
            "Strike": identity[3],
            "Option Type": identity[4],

            "Observation Count": len(
                observations
            ),

            "Movement Intervals": len(
                direction_results
            ),

            "Latest Combined Interpretation": (
                latest_combined
            ),

            "Momentum Evidence": (
                momentum_evidence
            ),

            "Momentum Sequence": (
                momentum_sequence
            ),

            "Momentum Confirmation": (
                momentum_confirmation
            ),

            "Status": momentum_confirmation.get(
                "Momentum Confirmation",
                "NOT_CONFIRMED",
            ),

            "Live Order": False,
            "Paper Trade": False,
        })

    return {
        "Status": "UNIFIED_MOMENTUM_COMPLETE",

        "Observation Count": observation_count,

        "Movement Intervals": (
            observation_count - 1
        ),

        "Contract Count": len(results),

        "Results": results,

        "Source": (
            "V21.2.15 Unified Observation Session"
        ),

        "New Market Observations": False,

        "Live Order": False,
        "Paper Trade": False,
    }