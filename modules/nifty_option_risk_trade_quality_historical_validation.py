"""
JKJ AI Trader
V12.9 Stage 4 — Historical Risk & Trade Quality Validation

Validates the complete historical evidence chain through V12.9.

This module does not generate a trading signal.
"""

from modules.nifty_option_movement_analyzer import analyze_option_movement
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

from modules.nifty_option_momentum_sequence import (
    evaluate_momentum_sequence,
)
from modules.nifty_option_momentum_evidence import (
    evaluate_momentum_evidence,
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

from modules.nifty_option_opportunity_evidence import (
    evaluate_opportunity_evidence,
)
from modules.nifty_option_opportunity_classification import (
    evaluate_opportunity_classification,
)
from modules.nifty_option_opportunity_strength import (
    evaluate_opportunity_strength,
)

from modules.nifty_option_risk_evidence import (
    evaluate_risk_evidence,
)
from modules.nifty_option_risk_classification import (
    evaluate_risk_classification,
)

from modules.nifty_option_trade_quality import (
    evaluate_trade_quality,
)


def validate_historical_risk_trade_quality(observations):
    """
    Validate historical observations through V12.9.
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

    first = observations[0]

    required_identity = {
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
    }

    missing_identity = [
        field for field in required_identity
        if field not in first
    ]

    if missing_identity:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing identity fields: {missing_identity}",
        }

    direction_results = []
    volume_oi_results = []
    relationship_results = []
    combined_results = []

    for index in range(1, len(observations)):
        previous = observations[index - 1]
        current = observations[index]

        analyzed = analyze_option_movement(
            previous,
            current,
        )

        direction = interpret_movement_direction(analyzed)

        volume_oi = interpret_volume_oi_behavior(analyzed)

        relationship = interpret_movement_relationship(
            direction
        )

        combined = combine_movement_interpretation(
            direction,
            volume_oi,
            relationship,
        )

        direction_results.append(direction)
        volume_oi_results.append(volume_oi)
        relationship_results.append(relationship)
        combined_results.append(combined)

    momentum_sequence = evaluate_momentum_sequence(
        direction_results
    )

    latest_combined = combined_results[-1]

    momentum_evidence = evaluate_momentum_evidence(
        latest_combined,
    )

    momentum_confirmation = evaluate_momentum_confirmation(
        momentum_evidence,
        momentum_sequence,
    )

    market_context_evidence = evaluate_market_context_evidence(
        momentum_confirmation
    )

    market_context_classification = (
        evaluate_market_context_classification(
            market_context_evidence
        )
    )

    momentum_context = evaluate_momentum_context(
        momentum_confirmation,
        market_context_classification,
    )

    opportunity_evidence = evaluate_opportunity_evidence(
        momentum_context
    )

    opportunity_classification = (
        evaluate_opportunity_classification(
            opportunity_evidence
        )
    )

    opportunity_strength = evaluate_opportunity_strength(
        opportunity_classification
    )

    risk_evidence = evaluate_risk_evidence(
        opportunity_strength
    )

    risk_classification = evaluate_risk_classification(
        risk_evidence
    )

    trade_quality = evaluate_trade_quality(
        risk_classification
    )

    if trade_quality.get("Status") != "CLASSIFIED":
        return {
            "Status": "REJECTED",
            "Reason": "Trade Quality evaluation failed",
        }

    return {
        "Status": "VALIDATED",

        "Trading Symbol": first["Trading Symbol"],
        "Underlying": first["Underlying"],
        "Expiry": first["Expiry"],
        "Strike": first["Strike"],
        "Option Type": first["Option Type"],

        "Observation Count": len(observations),
        "Movement Count": len(direction_results),

        "Option Direction": trade_quality["Option Direction"],
        "Momentum Persistence": momentum_sequence[
            "Persistence Status"
        ],
        "Momentum Confirmation": trade_quality[
            "Momentum Confirmation"
        ],

        "Market Context": trade_quality[
            "Market Context"
        ],
        "Movement Relationship": trade_quality[
            "Movement Relationship"
        ],
        "Momentum Context": trade_quality[
            "Momentum Context"
        ],

        "Opportunity Classification": trade_quality[
            "Opportunity Classification"
        ],
        "Opportunity Strength": trade_quality[
            "Opportunity Strength"
        ],

        "Risk Classification": trade_quality[
            "Risk Classification"
        ],
        "Trade Quality": trade_quality[
            "Trade Quality"
        ],
    }