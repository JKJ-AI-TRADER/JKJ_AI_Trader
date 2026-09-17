"""
JKJ AI Trader
NIFTY Option Momentum Historical Validation — V12.6 Stage 4

Purpose:
Validate the V12.6 momentum interpretation pipeline using
historical recorded NIFTY option observations.

Pipeline:
Recorded Observations
        ↓
V12.4 Movement Analysis
        ↓
V12.5 Direction
V12.5 Volume/OI
V12.5 Relationship
        ↓
V12.5 Combined Interpretation
        ↓
V12.6 Momentum Evidence
V12.6 Momentum Sequence
V12.6 Momentum Confirmation

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules
"""


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


def validate_historical_momentum(observations):
    """
    Validate V12.6 momentum behaviour across historical
    recorded observations.

    Observations must:
    - be dictionaries
    - have Status RECORDED
    - belong to the same option contract
    - be supplied in chronological order
    """

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list.",
        }

    if len(observations) < 4:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Reason": (
                "At least 4 recorded observations are required "
                "to produce 3 movement observations."
            ),
            "Observation Count": len(observations),
            "Required Observation Count": 4,
        }

    for observation in observations:
        if not isinstance(observation, dict):
            return {
                "Status": "REJECTED",
                "Reason": "Each observation must be a dictionary.",
            }

        if observation.get("Status") != "RECORDED":
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Every observation must have "
                    "Status RECORDED."
                ),
            }

    # ---------------------------------------------------------
    # Step 1: Analyze consecutive observations
    # ---------------------------------------------------------

    analyzed_movements = []

    for index in range(1, len(observations)):
        previous_observation = observations[index - 1]
        current_observation = observations[index]

        movement = analyze_option_movement(
            previous_observation,
            current_observation,
        )

        if movement.get("Status") != "ANALYZED":
            return {
                "Status": "REJECTED",
                "Reason": (
                    f"Movement analysis failed at "
                    f"observation pair {index}."
                ),
            }

        analyzed_movements.append(movement)

    # ---------------------------------------------------------
    # Step 2: Interpret all movement dimensions
    # ---------------------------------------------------------

    direction_results = []
    volume_oi_results = []
    relationship_results = []
    combined_results = []

    for movement in analyzed_movements:

        direction_result = interpret_movement_direction(
            movement
        )

        if direction_result.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Movement direction interpretation failed.",
            }

        volume_oi_result = interpret_volume_oi_behavior(
            movement
        )

        if volume_oi_result.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Volume/OI interpretation failed.",
            }

        relationship_result = interpret_movement_relationship(
            direction_result
        )

        if relationship_result.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Movement relationship interpretation failed.",
            }

        combined_result = combine_movement_interpretation(
            direction_result,
            volume_oi_result,
            relationship_result,
        )

        if combined_result.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Combined interpretation failed.",
            }

        direction_results.append(direction_result)
        volume_oi_results.append(volume_oi_result)
        relationship_results.append(relationship_result)
        combined_results.append(combined_result)

    # ---------------------------------------------------------
    # Step 3: Evaluate momentum persistence
    # ---------------------------------------------------------

    momentum_sequence = evaluate_momentum_sequence(
        direction_results
    )

    if momentum_sequence.get("Status") not in {
        "PERSISTENT",
        "NOT_PERSISTENT",
    }:
        return {
            "Status": "REJECTED",
            "Reason": "Momentum sequence evaluation failed.",
        }

    # ---------------------------------------------------------
    # Step 4: Evaluate latest observable evidence
    # ---------------------------------------------------------

    latest_combined = combined_results[-1]

    momentum_evidence = evaluate_momentum_evidence(
        latest_combined
    )

    if momentum_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum evidence evaluation failed.",
        }

    # ---------------------------------------------------------
    # Step 5: Evaluate momentum confirmation
    # ---------------------------------------------------------

    momentum_confirmation = evaluate_momentum_confirmation(
        momentum_evidence,
        momentum_sequence,
    )

    if momentum_confirmation.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum confirmation evaluation failed.",
        }

    # ---------------------------------------------------------
    # Final validation result
    # ---------------------------------------------------------

    return {
        "Status": "VALIDATED",
        "Trading Symbol": latest_combined.get(
            "Trading Symbol"
        ),
        "Underlying": latest_combined.get(
            "Underlying"
        ),
        "Expiry": latest_combined.get(
            "Expiry"
        ),
        "Strike": latest_combined.get(
            "Strike"
        ),
        "Option Type": latest_combined.get(
            "Option Type"
        ),
        "Observation Count": len(observations),
        "Movement Count": len(analyzed_movements),
        "Direction Sequence": momentum_sequence.get(
            "Direction Sequence"
        ),
        "Persistence Status": momentum_sequence.get(
            "Persistence Status"
        ),
        "Option Direction": momentum_evidence.get(
            "Option Direction"
        ),
        "NIFTY Direction": momentum_evidence.get(
            "NIFTY Direction"
        ),
        "Price Movement Evidence": momentum_evidence.get(
            "Price Movement Evidence"
        ),
        "Volume Evidence": momentum_evidence.get(
            "Volume Evidence"
        ),
        "Open Interest Evidence": momentum_evidence.get(
            "Open Interest Evidence"
        ),
        "Movement Relationship": momentum_evidence.get(
            "Movement Relationship"
        ),
        "Momentum Confirmation": momentum_confirmation.get(
            "Momentum Confirmation"
        ),
    }