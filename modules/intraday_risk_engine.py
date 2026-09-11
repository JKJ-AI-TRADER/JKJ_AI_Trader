"""
JKJ AI Intraday Risk Engine v0.1

Wisdom Before Wealth.

A strong setup is not enough.

Every intraday trade must first define:

- Entry Price
- Stop Loss
- Risk Per Trade
- Target Price
- Risk to Reward Ratio

Capital protection comes before profit.
"""


def analyse_intraday_risk(
    entry_price,
    stop_loss,
    target_price,
    setup_score,
    trading_allowed=True
):
    """
    Analyse whether an intraday trade has
    acceptable risk.

    Returns an explainable risk assessment.
    """

    reasons = []
    warnings = []

    # -----------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------

    if not trading_allowed:

        return {
            "Trade Allowed": False,
            "Risk Status": "MARKET NOT SUITABLE",
            "Risk Level": "HIGH",
            "Entry Price": entry_price,
            "Stop Loss": stop_loss,
            "Target Price": target_price,
            "Risk Percentage": 0,
            "Reward Percentage": 0,
            "Risk Reward Ratio": 0,
            "Reasons": [
                "The intraday market environment "
                "does not currently allow trading."
            ],
            "Warnings": []
        }

    if entry_price <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID ENTRY",
            "Risk Level": "HIGH",
            "Reasons": [
                "Entry price must be greater than zero."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # CALCULATE RISK
    # -----------------------------------------

    risk_amount = entry_price - stop_loss
    reward_amount = target_price - entry_price

    if risk_amount <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID STOP LOSS",
            "Risk Level": "HIGH",
            "Reasons": [
                "Stop loss must be below the entry "
                "price for a long trade."
            ],
            "Warnings": []
        }

    if reward_amount <= 0:

        return {
            "Trade Allowed": False,
            "Risk Status": "INVALID TARGET",
            "Risk Level": "HIGH",
            "Reasons": [
                "Target price must be above the entry "
                "price for a long trade."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # PERCENTAGES
    # -----------------------------------------

    risk_percentage = (
        risk_amount / entry_price
    ) * 100

    reward_percentage = (
        reward_amount / entry_price
    ) * 100

    risk_reward_ratio = (
        reward_amount / risk_amount
    )

    risk_percentage = round(
        risk_percentage,
        2
    )

    reward_percentage = round(
        reward_percentage,
        2
    )

    risk_reward_ratio = round(
        risk_reward_ratio,
        2
    )

    # -----------------------------------------
    # RISK CLASSIFICATION
    # -----------------------------------------

    if risk_percentage > 2:

        risk_level = "HIGH"

        warnings.append(
            "Stop-loss risk exceeds the preferred "
            "2% intraday limit."
        )

    elif risk_percentage > 1:

        risk_level = "MEDIUM"

        warnings.append(
            "Trade risk is above the preferred "
            "1% capital protection level."
        )

    else:

        risk_level = "LOW"

        reasons.append(
            "Stop-loss risk is within the preferred "
            "intraday range."
        )

    # -----------------------------------------
    # RISK / REWARD EVALUATION
    # -----------------------------------------

    if risk_reward_ratio < 1.5:

        warnings.append(
            "Risk-to-reward ratio is below the "
            "preferred minimum of 1.5."
        )

    else:

        reasons.append(
            "Risk-to-reward ratio is acceptable."
        )

    # -----------------------------------------
    # SETUP QUALITY
    # -----------------------------------------

    if setup_score < 60:

        warnings.append(
            "Trade setup strength is not sufficient."
        )

    else:

        reasons.append(
            "Trade setup strength is acceptable."
        )

    # -----------------------------------------
    # FINAL TRADE DECISION
    # -----------------------------------------

    trade_allowed = True

    if risk_level == "HIGH":

        trade_allowed = False

    if risk_reward_ratio < 1.5:

        trade_allowed = False

    if setup_score < 60:

        trade_allowed = False

    if trade_allowed:

        risk_status = "ACCEPTABLE"

        reasons.append(
            "The trade meets the minimum JKJ "
            "intraday risk requirements."
        )

    else:

        risk_status = "NOT ACCEPTABLE"

        warnings.append(
            "The trade should not be taken until "
            "risk conditions improve."
        )

    return {
        "Trade Allowed": trade_allowed,
        "Risk Status": risk_status,
        "Risk Level": risk_level,
        "Entry Price": round(entry_price, 2),
        "Stop Loss": round(stop_loss, 2),
        "Target Price": round(target_price, 2),
        "Risk Percentage": risk_percentage,
        "Reward Percentage": reward_percentage,
        "Risk Reward Ratio": risk_reward_ratio,
        "Reasons": reasons,
        "Warnings": warnings
    }