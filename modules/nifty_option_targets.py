"""
JKJ AI Trader
V14.4 — Targets 1–3

Establishes three risk-based target levels
from the validated V14.3 stop-loss structure.

Target 1 = 1R
Target 2 = 2R
Target 3 = 3R

This module does not make exit decisions,
calculate position size, or place orders.
"""


def evaluate_targets(stop_loss_price_data):
    """
    Calculate Targets 1–3 from validated stop-loss data.
    """

    if not isinstance(stop_loss_price_data, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Stop-Loss Price data must be a dictionary",
        }

    if stop_loss_price_data.get("Status") != "STOP_VALIDATED":
        return {
            "Status": "REJECTED",
            "Reason": "Stop-Loss Price must be STOP_VALIDATED",
        }

    required_fields = {
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Option Direction",
        "Entry Qualification",
        "Entry Risk Context",
        "Stop-Loss Context",
        "Entry Price",
        "Stop Price",
        "Stop Distance",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in stop_loss_price_data
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    entry_price = stop_loss_price_data["Entry Price"]
    stop_price = stop_loss_price_data["Stop Price"]
    stop_distance = stop_loss_price_data["Stop Distance"]

    if not isinstance(entry_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Entry Price must be numeric",
        }

    if not isinstance(stop_price, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Stop Price must be numeric",
        }

    if not isinstance(stop_distance, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "Stop Distance must be numeric",
        }

    if entry_price <= 0 or stop_price <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Entry Price and Stop Price must be positive",
        }

    if stop_price >= entry_price:
        return {
            "Status": "REJECTED",
            "Reason": "Stop Price must be below Entry Price",
        }

    if stop_distance <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Stop Distance must be greater than zero",
        }

    target_1 = entry_price + stop_distance
    target_2 = entry_price + (2 * stop_distance)
    target_3 = entry_price + (3 * stop_distance)

    return {
        "Status": "TARGETS_VALIDATED",

        "Trading Symbol": stop_loss_price_data["Trading Symbol"],
        "Underlying": stop_loss_price_data["Underlying"],
        "Expiry": stop_loss_price_data["Expiry"],
        "Strike": stop_loss_price_data["Strike"],
        "Option Type": stop_loss_price_data["Option Type"],

        "Option Direction": stop_loss_price_data["Option Direction"],
        "Entry Qualification": stop_loss_price_data[
            "Entry Qualification"
        ],
        "Entry Risk Context": stop_loss_price_data[
            "Entry Risk Context"
        ],
        "Stop-Loss Context": stop_loss_price_data[
            "Stop-Loss Context"
        ],

        "Entry Price": entry_price,
        "Stop Price": stop_price,
        "Stop Distance": stop_distance,

        "Target 1": target_1,
        "Target 2": target_2,
        "Target 3": target_3,
    }