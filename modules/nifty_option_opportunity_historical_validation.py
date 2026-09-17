"""
JKJ AI Trader
V12.8 Stage 4 — Historical Opportunity Validation

Validates the complete V12.4 → V12.8 opportunity-analysis chain
using recorded historical observations.

This module does not generate a trading signal.
"""

from modules.nifty_option_movement_analyzer import analyze_option_movement
from modules.nifty_option_movement_direction import interpret_movement_direction
from modules.nifty_option_volume_oi_behavior import interpret_volume_oi_behavior
from modules.nifty_option_movement_relationship import (
    interpret_movement_relationship,
)
from modules.nifty_option_combined_interpretation import (
    combine_movement_interpretation,
)
from modules.nifty_option_momentum_evidence import evaluate_momentum_evidence
from modules.nifty_option_momentum_sequence import evaluate_momentum_sequence
from modules.nifty_option_momentum_confirmation import (
    evaluate_momentum_confirmation,
)
from modules.nifty_option_market_context_evidence import (
    evaluate_market_context_evidence,
)
from modules.nifty_option_market_context_classification import (
    evaluate_market_context_classification,
)
from modules.nifty_option_momentum_context import evaluate_momentum_context
from modules.nifty_option_opportunity_evidence import (
    evaluate_opportunity_evidence,
)
from modules.nifty_option_opportunity_classification import (
    evaluate_opportunity_classification,
)
from modules.nifty_option_opportunity_strength import (
    evaluate_opportunity_strength,
)


def validate_historical_opportunity(observations):
    """
    Run the complete historical V12.4 → V12.8 pipeline.
    """

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list",
        }

    if len(observations) < 4:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Reason": "At least 4 observations are required",
        }

    for observation in observations:
        if not isinstance(observation, dict):
            return {
                "Status": "REJECTED",
                "Reason": "Each observation must be a dictionary",
            }

        if observation.get("Status") != "RECORDED":
            return {
                "Status": "REJECTED",
                "Reason": "All observations must have Status RECORDED",
            }

    movement_results = []
    direction_results = []
    volume_oi_results = []
    relationship_results = []
    combined_results = []

    for index in range(1, len(observations)):

        analyzed = analyze_option_movement(
            observations[index - 1],
            observations[index],
        )

        if analyzed.get("Status") != "ANALYZED":
            return {
                "Status": "REJECTED",
                "Reason": "Movement analysis failed",
            }

        direction = interpret_movement_direction(analyzed)

        if direction.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Movement direction interpretation failed",
            }

        volume_oi = interpret_volume_oi_behavior(analyzed)

        if volume_oi.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Volume/OI interpretation failed",
            }

        relationship = interpret_movement_relationship(direction)

        if relationship.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Movement relationship interpretation failed",
            }

        combined = combine_movement_interpretation(
            direction,
            volume_oi,
            relationship,
        )

        if combined.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Reason": "Combined interpretation failed",
            }

        movement_results.append(analyzed)
        direction_results.append(direction)
        volume_oi_results.append(volume_oi)
        relationship_results.append(relationship)
        combined_results.append(combined)

    momentum_sequence = evaluate_momentum_sequence(direction_results)

    if momentum_sequence.get("Status") not in {
        "PERSISTENT",
        "NOT_PERSISTENT",
    }:
        return {
            "Status": "REJECTED",
            "Reason": "Momentum sequence evaluation failed",
        }

    latest_combined = combined_results[-1]

    momentum_evidence = evaluate_momentum_evidence(
        latest_combined
    )

    if momentum_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum evidence evaluation failed",
        }

    momentum_confirmation = evaluate_momentum_confirmation(
        momentum_evidence,
        momentum_sequence,
    )

    if momentum_confirmation.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum confirmation evaluation failed",
        }

    market_context_evidence = evaluate_market_context_evidence(
        momentum_confirmation
    )

    if market_context_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Market context evidence evaluation failed",
        }

    market_context_classification = (
        evaluate_market_context_classification(
            market_context_evidence
        )
    )

    if market_context_classification.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Market context classification failed",
        }

    momentum_context = evaluate_momentum_context(
        momentum_confirmation,
        market_context_classification,
    )

    if momentum_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum context evaluation failed",
        }

    opportunity_evidence = evaluate_opportunity_evidence(
        momentum_context
    )

    if opportunity_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity evidence evaluation failed",
        }

    opportunity_classification = evaluate_opportunity_classification(
        opportunity_evidence
    )

    if opportunity_classification.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity classification failed",
        }

    opportunity_strength = evaluate_opportunity_strength(
        opportunity_classification
    )

    if opportunity_strength.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Opportunity strength evaluation failed",
        }

    return {
        "Status": "VALIDATED",

        "Trading Symbol": opportunity_strength["Trading Symbol"],
        "Underlying": opportunity_strength["Underlying"],
        "Expiry": opportunity_strength["Expiry"],
        "Strike": opportunity_strength["Strike"],
        "Option Type": opportunity_strength["Option Type"],

        "Observation Count": len(observations),
        "Movement Count": len(movement_results),

        "Option Direction": opportunity_strength["Option Direction"],
        "Momentum Persistence": momentum_sequence[
            "Persistence Status"
        ],
        "Momentum Confirmation": opportunity_strength[
            "Momentum Confirmation"
        ],

        "Market Context": opportunity_strength["Market Context"],
        "Movement Relationship": opportunity_strength[
            "Movement Relationship"
        ],
        "Momentum Context": opportunity_strength["Momentum Context"],

        "Opportunity Classification": opportunity_strength[
            "Opportunity Classification"
        ],
        "Opportunity Strength": opportunity_strength[
            "Opportunity Strength"
        ],
    }