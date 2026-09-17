"""
JKJ AI Trader
V14.3 — Stop-Loss Price

Establishes an evidence-based stop-loss price
from recent option price structure.

This module does not calculate targets,
position size, or place orders.
"""


def evaluate_stop_loss_price(
    stop_loss_context,
    entry_price,
    price_history,
):
    """
    Establish a stop-loss price from recent option prices.
    """

    if not isinstance(stop_loss_context, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Stop-Loss Context must be a dictionary",
        }

    if stop_loss_context.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Stop-Loss Context status must be EVALUATED",
        }

    required_fields = {
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Option Direction",
        "Entry Qualification",
        "Risk Classification",
        "Trade Quality",
        "Entry Risk Context",
        "Stop-Loss Context",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in stop_loss_context
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    if not isinstance(entry_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Entry Price must be numeric",
        }

    if entry_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Entry Price must be greater than zero",
        }

    if not isinstance(price_history, list):
        return {
            "Status": "REJECTED",
            "Reason": "Price History must be a list",
        }

    if len(price_history) < 3:
        return {
            "Status": "INSUFFICIENT_PRICE_HISTORY",
            "Reason": "At least 3 price observations are required",
        }

    stop_context = stop_loss_context["Stop-Loss Context"]

    if stop_context != "STOP_SUPPORTED":
        return {
            "Status": "STOP_NOT_ESTABLISHED",
            "Reason": (
                "Stop-loss price requires STOP_SUPPORTED context"
            ),
        }

    if not all(
        isinstance(price, (int, float)) and price > 0
        for price in price_history
    ):
        return {
            "Status": "REJECTED",
            "Reason": "Price History contains invalid prices",
        }

    # Recent structural low for a long option position.
    structural_low = min(price_history)

    if structural_low >= entry_price:
        return {
            "Status": "STOP_REJECTED",
            "Reason": (
                "Structural low must be below the entry price"
            ),
            "Entry Price": entry_price,
            "Structural Low": structural_low,
        }

    stop_distance = entry_price - structural_low

    return {
        "Status": "STOP_VALIDATED",

        "Trading Symbol": stop_loss_context["Trading Symbol"],
        "Underlying": stop_loss_context["Underlying"],
        "Expiry": stop_loss_context["Expiry"],
        "Strike": stop_loss_context["Strike"],
        "Option Type": stop_loss_context["Option Type"],

        "Option Direction": stop_loss_context["Option Direction"],
        "Entry Qualification": stop_loss_context[
            "Entry Qualification"
        ],
        "Entry Risk Context": stop_loss_context[
            "Entry Risk Context"
        ],
        "Stop-Loss Context": stop_context,

        "Entry Price": entry_price,
        "Structural Low": structural_low,
        "Stop Price": structural_low,
        "Stop Distance": stop_distance,
    }