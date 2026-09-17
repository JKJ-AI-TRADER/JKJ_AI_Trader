"""
JKJ AI Trader
V13–V14 Historical Decision & Risk Validation

Purpose:
Validate the complete historical evidence chain from
V12.4 movement analysis through V14.5 exit qualification.

This module does NOT:
- place orders
- connect to live markets
- generate live trading signals
- modify main.py
- modify existing V12 modules
- modify existing V13/V14 modules

Historical entry rule:
- Latest observation Current Price is treated as entry price.
- Earlier observation prices are used as stop-loss history.
- This avoids using the entry observation itself to establish
  the structural low.
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

from modules.nifty_option_decision_context import (
    evaluate_decision_context,
)
from modules.nifty_option_entry_qualification import (
    evaluate_entry_qualification,
)

from modules.nifty_option_entry_risk_context import (
    evaluate_entry_risk_context,
)
from modules.nifty_option_stop_loss_context import (
    evaluate_stop_loss_context,
)
from modules.nifty_option_stop_loss_price import (
    evaluate_stop_loss_price,
)
from modules.nifty_option_targets import (
    evaluate_targets,
)
from modules.nifty_option_exit_qualification import (
    evaluate_exit_qualification,
)


def _reject(reason):
    return {
        "Status": "REJECTED",
        "Reason": reason,
    }


def validate_historical_v13_v14(observations):
    """
    Validate historical observations through V13 and V14.
    """

    if not isinstance(observations, list):
        return _reject("Observations must be a list")

    if len(observations) < 4:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Reason": "At least 4 observations are required",
        }

    for observation in observations:
        if not isinstance(observation, dict):
            return _reject(
                "Each observation must be a dictionary"
            )

        if observation.get("Status") != "RECORDED":
            return _reject(
                "All observations must have Status RECORDED"
            )

    first = observations[0]

    identity_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
    ]

    for field in identity_fields:
        if field not in first:
            return _reject(
                f"Missing identity field: {field}"
            )

    # ---------------------------------------------------------
    # V12.4 → V12.5
    # ---------------------------------------------------------

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

        if analyzed.get("Status") != "ANALYZED":
            return _reject(
                f"V12.4 failed at movement {index}"
            )

        direction = interpret_movement_direction(
            analyzed
        )

        if direction.get("Status") != "INTERPRETED":
            return _reject(
                f"V12.5 direction failed at movement {index}"
            )

        volume_oi = interpret_volume_oi_behavior(
            analyzed
        )

        if volume_oi.get("Status") != "INTERPRETED":
            return _reject(
                f"V12.5 volume/OI failed at movement {index}"
            )

        relationship = interpret_movement_relationship(
            direction
        )

        if relationship.get("Status") != "INTERPRETED":
            return _reject(
                f"V12.5 relationship failed at movement {index}"
            )

        combined = combine_movement_interpretation(
            direction,
            volume_oi,
            relationship,
        )

        if combined.get("Status") != "INTERPRETED":
            return _reject(
                f"V12.5 combined interpretation failed "
                f"at movement {index}"
            )

        direction_results.append(direction)
        volume_oi_results.append(volume_oi)
        relationship_results.append(relationship)
        combined_results.append(combined)

    # ---------------------------------------------------------
    # V12.6 Momentum
    # ---------------------------------------------------------

    momentum_sequence = evaluate_momentum_sequence(
        direction_results
    )

    if momentum_sequence.get("Status") not in {
        "PERSISTENT",
        "NOT_PERSISTENT",
    }:
        return _reject(
            "V12.6 momentum sequence failed"
        )

    latest_combined = combined_results[-1]

    momentum_evidence = evaluate_momentum_evidence(
        latest_combined
    )

    if momentum_evidence.get("Status") != "EVALUATED":
        return _reject(
            "V12.6 momentum evidence failed"
        )

    momentum_confirmation = evaluate_momentum_confirmation(
        momentum_evidence,
        momentum_sequence,
    )

    if momentum_confirmation.get("Status") != "EVALUATED":
        return _reject(
            "V12.6 momentum confirmation failed"
        )

    # ---------------------------------------------------------
    # V12.7 Market Context
    # ---------------------------------------------------------

    market_context_evidence = (
        evaluate_market_context_evidence(
            momentum_confirmation
        )
    )

    if market_context_evidence.get("Status") != "EVALUATED":
        return _reject(
            "V12.7 market context evidence failed"
        )

    market_context_classification = (
        evaluate_market_context_classification(
            market_context_evidence
        )
    )

    if market_context_classification.get(
        "Status"
    ) != "CLASSIFIED":
        return _reject(
            "V12.7 market context classification failed"
        )

    momentum_context = evaluate_momentum_context(
        momentum_confirmation,
        market_context_classification,
    )

    if momentum_context.get("Status") != "EVALUATED":
        return _reject(
            "V12.7 momentum context failed"
        )

    # ---------------------------------------------------------
    # V12.8 Opportunity
    # ---------------------------------------------------------

    opportunity_evidence = evaluate_opportunity_evidence(
        momentum_context
    )

    if opportunity_evidence.get("Status") != "EVALUATED":
        return _reject(
            "V12.8 opportunity evidence failed"
        )

    opportunity_classification = (
        evaluate_opportunity_classification(
            opportunity_evidence
        )
    )

    if opportunity_classification.get(
        "Status"
    ) != "CLASSIFIED":
        return _reject(
            "V12.8 opportunity classification failed"
        )

    opportunity_strength = evaluate_opportunity_strength(
        opportunity_classification
    )

    if opportunity_strength.get("Status") != "EVALUATED":
        return _reject(
            "V12.8 opportunity strength failed"
        )

    # ---------------------------------------------------------
    # V12.9 Risk / Trade Quality
    # ---------------------------------------------------------

    risk_evidence = evaluate_risk_evidence(
        opportunity_strength
    )

    if risk_evidence.get("Status") != "EVALUATED":
        return _reject(
            "V12.9 risk evidence failed"
        )

    risk_classification = evaluate_risk_classification(
        risk_evidence
    )

    if risk_classification.get("Status") != "CLASSIFIED":
        return _reject(
            "V12.9 risk classification failed"
        )

    trade_quality = evaluate_trade_quality(
        risk_classification
    )

    if trade_quality.get("Status") != "CLASSIFIED":
        return _reject(
            "V12.9 trade quality failed"
        )

    # ---------------------------------------------------------
    # V13 Decision
    # ---------------------------------------------------------

    decision_context = evaluate_decision_context(
        trade_quality
    )

    if decision_context.get("Status") != "EVALUATED":
        return _reject(
            "V13.1 decision context failed"
        )

    entry_qualification = evaluate_entry_qualification(
        decision_context
    )

    if entry_qualification.get("Status") != "QUALIFIED":
        return _reject(
            "V13.2 entry qualification failed"
        )

    # ---------------------------------------------------------
    # V14.1 Entry Risk
    # ---------------------------------------------------------

    entry_risk_context = evaluate_entry_risk_context(
        entry_qualification
    )

    if entry_risk_context.get("Status") != "EVALUATED":
        return _reject(
            "V14.1 entry risk context failed"
        )

    # ---------------------------------------------------------
    # V14.2 Stop-Loss Context
    # ---------------------------------------------------------

    stop_loss_context = evaluate_stop_loss_context(
        entry_risk_context
    )

    if stop_loss_context.get("Status") != "EVALUATED":
        return _reject(
            "V14.2 stop-loss context failed"
        )

    # ---------------------------------------------------------
    # V14.3 Stop-Loss Price
    # ---------------------------------------------------------

    entry_price = observations[-1]["Current Price"]

    stop_price_history = [
        observation["Current Price"]
        for observation in observations[:-1]
    ]

    stop_loss_price = evaluate_stop_loss_price(
        stop_loss_context,
        entry_price,
        stop_price_history,
    )

    if stop_loss_price.get("Status") != "STOP_VALIDATED":
        return {
            "Status": "VALIDATED_TO_STOP_CONTEXT",
            "Reason": (
                "Historical setup reached V14.2, "
                "but a valid stop-loss price was not established."
            ),
            "Trading Symbol": first["Trading Symbol"],
            "Entry Qualification": entry_qualification[
                "Entry Qualification"
            ],
            "Entry Risk Context": entry_risk_context[
                "Entry Risk Context"
            ],
            "Stop-Loss Context": stop_loss_context[
                "Stop-Loss Context"
            ],
            "Entry Price": entry_price,
        }

    # ---------------------------------------------------------
    # V14.4 Targets
    # ---------------------------------------------------------

    targets = evaluate_targets(
        stop_loss_price
    )

    if targets.get("Status") != "TARGETS_VALIDATED":
        return _reject(
            "V14.4 targets failed"
        )

    # ---------------------------------------------------------
    # V14.5 Exit Qualification
    # ---------------------------------------------------------

    exit_qualification = evaluate_exit_qualification(
        targets
    )

    if exit_qualification.get("Status") != "EVALUATED":
        return _reject(
            "V14.5 exit qualification failed"
        )

    # ---------------------------------------------------------
    # Final validated result
    # ---------------------------------------------------------

    return {
        "Status": "VALIDATED",

        "Trading Symbol": first["Trading Symbol"],
        "Underlying": first["Underlying"],
        "Expiry": first["Expiry"],
        "Strike": first["Strike"],
        "Option Type": first["Option Type"],

        "Observation Count": len(observations),
        "Movement Count": len(direction_results),

        "Option Direction": trade_quality[
            "Option Direction"
        ],

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

        "Entry Qualification": entry_qualification[
            "Entry Qualification"
        ],

        "Entry Risk Context": entry_risk_context[
            "Entry Risk Context"
        ],

        "Stop-Loss Context": stop_loss_context[
            "Stop-Loss Context"
        ],

        "Entry Price": stop_loss_price[
            "Entry Price"
        ],

        "Structural Low": stop_loss_price[
            "Structural Low"
        ],

        "Stop Price": stop_loss_price[
            "Stop Price"
        ],

        "Stop Distance": stop_loss_price[
            "Stop Distance"
        ],

        "Target 1": targets["Target 1"],
        "Target 2": targets["Target 2"],
        "Target 3": targets["Target 3"],

        "Risk Reward 1": exit_qualification[
            "Risk Reward 1"
        ],

        "Risk Reward 2": exit_qualification[
            "Risk Reward 2"
        ],

        "Risk Reward 3": exit_qualification[
            "Risk Reward 3"
        ],

        "Exit Structure": exit_qualification[
            "Exit Structure"
        ],
    }