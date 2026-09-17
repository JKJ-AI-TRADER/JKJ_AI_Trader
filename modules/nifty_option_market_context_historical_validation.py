"""
JKJ AI Trader
NIFTY Option Market Context Historical Validation — V12.7 Stage 4

Purpose:
Validate the V12.6 momentum and V12.7 market-context
interpretation pipeline using historical recorded observations.

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

from modules.nifty_option_market_context_evidence import (
    evaluate_market_context_evidence,
)

from modules.nifty_option_market_context_classification import (
    evaluate_market_context_classification,
)

from modules.nifty_option_momentum_context import (
    evaluate_momentum_context,
)


def validate_historical_market_context(observations):
    """
    Validate the complete V12.6 → V12.7 pipeline
    using historical recorded observations.
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
    # Step 1: V12.4 movement analysis
    # ---------------------------------------------------------

    analyzed_movements = []

    for index in range(1, len(observations)):

        movement = analyze_option_movement(
            observations[index - 1],
            observations[index],
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
    # Step 2: V12.5 interpretation
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
    # Step 3: V12.6 momentum sequence
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
    # Step 4: V12.6 latest evidence
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
    # Step 5: V12.6 momentum confirmation
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
    # Step 6: V12.7 market context evidence
    # ---------------------------------------------------------

    context_evidence = evaluate_market_context_evidence(
        momentum_confirmation
    )

    if context_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Market context evidence evaluation failed.",
        }

    # ---------------------------------------------------------
    # Step 7: V12.7 context classification
    # ---------------------------------------------------------

    context_classification = (
        evaluate_market_context_classification(
            context_evidence
        )
    )

    if context_classification.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Market context classification failed.",
        }

    # ---------------------------------------------------------
    # Step 8: V12.7 momentum + context
    # ---------------------------------------------------------

    momentum_context = evaluate_momentum_context(
        momentum_confirmation,
        context_classification,
    )

    if momentum_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum context evaluation failed.",
        }

    # ---------------------------------------------------------
    # Final validation result
    # ---------------------------------------------------------

    return {
        "Status": "VALIDATED",
        "Trading Symbol": momentum_context.get(
            "Trading Symbol"
        ),
        "Underlying": momentum_context.get(
            "Underlying"
        ),
        "Expiry": momentum_context.get(
            "Expiry"
        ),
        "Strike": momentum_context.get(
            "Strike"
        ),
        "Option Type": momentum_context.get(
            "Option Type"
        ),
        "Observation Count": len(observations),
        "Movement Count": len(analyzed_movements),
        "Option Direction": momentum_context.get(
            "Option Direction"
        ),
        "Persistence Status": momentum_confirmation.get(
            "Persistence Status"
        ),
        "Momentum Confirmation": momentum_context.get(
            "Momentum Confirmation"
        ),
        "Market Context": momentum_context.get(
            "Market Context"
        ),
        "Movement Relationship": momentum_context.get(
            "Movement Relationship"
        ),
        "Momentum Context": momentum_context.get(
            "Momentum Context"
        ),
    }