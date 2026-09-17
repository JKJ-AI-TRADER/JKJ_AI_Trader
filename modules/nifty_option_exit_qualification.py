"""
JKJ AI Trader
V14.5 — Risk/Reward + Exit Qualification

Evaluates the validated Entry, Stop-Loss and Target structure.

This module does not place orders or execute exits.
"""


def evaluate_exit_qualification(target_data):
    """
    Evaluate the V14.4 target structure for
    risk/reward and exit qualification.
    """

    if not isinstance(target_data, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Target data must be a dictionary",
        }

    if target_data.get("Status") != "TARGETS_VALIDATED":
        return {
            "Status": "REJECTED",
            "Reason": "Targets must be TARGETS_VALIDATED",
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
        "Target 1",
        "Target 2",
        "Target 3",
    }

    missing_fields = [
        field
        for field in required_fields
        if field not in target_data
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": f"Missing required fields: {missing_fields}",
        }

    entry_price = target_data["Entry Price"]
    stop_price = target_data["Stop Price"]
    stop_distance = target_data["Stop Distance"]
    target_1 = target_data["Target 1"]
    target_2 = target_data["Target 2"]
    target_3 = target_data["Target 3"]

    numeric_values = {
        "Entry Price": entry_price,
        "Stop Price": stop_price,
        "Stop Distance": stop_distance,
        "Target 1": target_1,
        "Target 2": target_2,
        "Target 3": target_3,
    }

    if not all(
        isinstance(value, (int, float))
        for value in numeric_values.values()
    ):
        return {
            "Status": "REJECTED",
            "Reason": "All price and risk values must be numeric",
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

    if not (
        target_1 > entry_price
        and target_2 > target_1
        and target_3 > target_2
    ):
        return {
            "Status": "EXIT_STRUCTURE_NOT_SUPPORTED",
            "Reason": "Targets must increase above the entry price",
        }

    reward_1 = target_1 - entry_price
    reward_2 = target_2 - entry_price
    reward_3 = target_3 - entry_price

    risk_reward_1 = reward_1 / stop_distance
    risk_reward_2 = reward_2 / stop_distance
    risk_reward_3 = reward_3 / stop_distance

    entry_qualification = target_data["Entry Qualification"]

    if entry_qualification == "ENTRY_QUALIFIED":
        exit_structure = "EXIT_STRUCTURE_SUPPORTED"

    elif entry_qualification == "ENTRY_DEVELOPING":
        exit_structure = "EXIT_STRUCTURE_DEVELOPING"

    else:
        exit_structure = "EXIT_STRUCTURE_NOT_SUPPORTED"

    return {
        "Status": "EVALUATED",

        "Trading Symbol": target_data["Trading Symbol"],
        "Underlying": target_data["Underlying"],
        "Expiry": target_data["Expiry"],
        "Strike": target_data["Strike"],
        "Option Type": target_data["Option Type"],

        "Option Direction": target_data["Option Direction"],
        "Entry Qualification": entry_qualification,
        "Entry Risk Context": target_data["Entry Risk Context"],
        "Stop-Loss Context": target_data["Stop-Loss Context"],

        "Entry Price": entry_price,
        "Stop Price": stop_price,
        "Stop Distance": stop_distance,

        "Target 1": target_1,
        "Target 2": target_2,
        "Target 3": target_3,

        "Risk Reward 1": risk_reward_1,
        "Risk Reward 2": risk_reward_2,
        "Risk Reward 3": risk_reward_3,

        "Exit Structure": exit_structure,
    }