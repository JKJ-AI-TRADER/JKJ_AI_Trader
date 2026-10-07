"""
JKJ AI Trader
V21.2.14 — Real-Market Risk + Stop-Loss Validation

Bridges V21.2.13 Decision/Entry Qualification into
the existing V14.1, V14.2 and V14.3 risk/stop-loss
architecture.

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.nifty_option_entry_risk_context import (
    evaluate_entry_risk_context,
)

from modules.nifty_option_stop_loss_context import (
    evaluate_stop_loss_context,
)

from modules.nifty_option_stop_loss_price import (
    evaluate_stop_loss_price,
)


def evaluate_real_market_risk_stop(
    decision_entry_result,
    observations,
):
    """
    Evaluate a V21.2.13 decision against the existing
    V14.1 -> V14.2 -> V14.3 risk/stop-loss chain.

    observations:
        List of real-market option observation records.
    """

    if not isinstance(decision_entry_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Decision/Entry result must be a dictionary"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if decision_entry_result.get("Status") != (
        "DECISION_ENTRY_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Decision/Entry status must be "
                "DECISION_ENTRY_COMPLETE"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list",
            "Live Order": False,
            "Paper Trade": False,
        }

    if len(observations) < 3:
        return {
            "Status": "INSUFFICIENT_PRICE_HISTORY",
            "Reason": (
                "At least 3 observations are required "
                "for V14.3 stop-loss validation"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # Extract the original V13.2 Entry Qualification result
    # ---------------------------------------------------------

    entry_qualification = decision_entry_result.get(
        "Entry Qualification Result"
    )

    if not isinstance(entry_qualification, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "V21.2.13 Entry Qualification Result "
                "is missing or invalid"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # V13.2 → V14.1
    # ---------------------------------------------------------

    entry_risk_context = evaluate_entry_risk_context(
        entry_qualification
    )

    if entry_risk_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "V14.1 Entry Risk Context rejected "
                "the V21.2.13 Entry Qualification"
            ),
            "Entry Risk Context": entry_risk_context,
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # V14.1 → V14.2
    # ---------------------------------------------------------

    stop_loss_context = evaluate_stop_loss_context(
        entry_risk_context
    )

    if stop_loss_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "V14.2 Stop-Loss Context rejected "
                "the V14.1 result"
            ),
            "Entry Risk Context": entry_risk_context,
            "Stop-Loss Context": stop_loss_context,
            "Live Order": False,
            "Paper Trade": False,
        }

    # ---------------------------------------------------------
    # Extract actual observed option prices
    # ---------------------------------------------------------

    price_history = []

    for observation in observations:

        if not isinstance(observation, dict):
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation history contains "
                    "a non-dictionary item"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

        if observation.get("Status") != "RECORDED":
            return {
                "Status": "REJECTED",
                "Reason": (
                    "All observations must have "
                    "Status RECORDED"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

        price = observation.get("Current Price")

        if not isinstance(price, (int, float)):
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation is missing a valid "
                    "Current Price"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

        price_history.append(price)

    # ---------------------------------------------------------
    # Validate identity consistency
    # ---------------------------------------------------------

    decision_symbol = decision_entry_result.get(
        "Trading Symbol"
    )

    for observation in observations:

        if observation.get("Trading Symbol") != decision_symbol:
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation Trading Symbol does not "
                    "match Decision/Entry Trading Symbol"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

    # ---------------------------------------------------------
    # Latest observed price becomes candidate entry price
    # ---------------------------------------------------------

    entry_price = price_history[-1]

    # ---------------------------------------------------------
    # V14.3 Stop-Loss Price
    # ---------------------------------------------------------

    stop_loss_price = evaluate_stop_loss_price(
        stop_loss_context,
        entry_price,
        price_history,
    )

    # ---------------------------------------------------------
    # Safe result
    # ---------------------------------------------------------

    return {
        "Status": "RISK_STOP_COMPLETE",

        "Trading Symbol": decision_entry_result[
            "Trading Symbol"
        ],
        "Underlying": decision_entry_result[
            "Underlying"
        ],
        "Expiry": decision_entry_result[
            "Expiry"
        ],
        "Strike": decision_entry_result[
            "Strike"
        ],
        "Option Type": decision_entry_result[
            "Option Type"
        ],

        "Option Direction": decision_entry_result[
            "Option Direction"
        ],
        "Entry Qualification": decision_entry_result[
            "Entry Qualification"
        ],

        "Risk Classification": decision_entry_result[
            "Risk Classification"
        ],
        "Trade Quality": decision_entry_result[
            "Trade Quality"
        ],

        "Stop-Loss Context": stop_loss_context[
            "Stop-Loss Context"
        ],

        "Observation Count": len(observations),
        "Price History": price_history,
        "Entry Price": entry_price,

        "Stop-Loss Result": stop_loss_price,

        "Live Order": False,
        "Paper Trade": False,
    }