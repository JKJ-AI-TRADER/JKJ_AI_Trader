"""
JKJ AI Trader
Intraday Option Candidate Enrichment V6

Purpose:
Combine an option candidate with the additional information
needed before final momentum and entry evaluation.

This module does NOT:
- place orders
- connect to Zerodha
- make BUY/SELL decisions
- modify the Momentum Engine
- modify main.py
"""


def enrich_option_candidate(
    option_data,
    underlying_data,
    spread_percentage=None,
    remaining_profit_percentage=None,
    risk_reward_ratio=None,
):
    """
    Enrich an option candidate with underlying confirmation,
    liquidity, profit potential and risk/reward information.

    Parameters
    ----------
    option_data : dict
        Standardized option market data.

    underlying_data : dict
        Current underlying NIFTY market information.

    spread_percentage : float, optional
        Current bid/ask spread percentage.

    remaining_profit_percentage : float, optional
        Estimated remaining profit potential.

    risk_reward_ratio : float, optional
        Estimated risk/reward ratio.

    Returns
    -------
    dict
        Enriched option candidate.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not isinstance(option_data, dict):
        return {
            "Status": "INVALID",
            "Reasons": [
                "Option data must be a dictionary."
            ],
        }

    if not isinstance(underlying_data, dict):
        return {
            "Status": "INVALID",
            "Reasons": [
                "Underlying data must be a dictionary."
            ],
        }

    required_option_fields = [
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Current Price",
        "Volume",
    ]

    missing_option_fields = [
        field
        for field in required_option_fields
        if field not in option_data
    ]

    if missing_option_fields:
        return {
            "Status": "INVALID",
            "Reasons": [
                f"Missing option fields: "
                f"{missing_option_fields}"
            ],
        }

    required_underlying_fields = [
        "Current Price",
        "MA20",
        "MA50",
        "RSI",
    ]

    missing_underlying_fields = [
        field
        for field in required_underlying_fields
        if field not in underlying_data
    ]

    if missing_underlying_fields:
        return {
            "Status": "INVALID",
            "Reasons": [
                f"Missing underlying fields: "
                f"{missing_underlying_fields}"
            ],
        }

    # ---------------------------------------------------------
    # OPTION VALIDATION
    # ---------------------------------------------------------

    if option_data["Underlying"] != "NIFTY":
        return {
            "Status": "INVALID",
            "Reasons": [
                "Only NIFTY options are supported in V6."
            ],
        }

    if option_data["Option Type"] not in (
        "CE",
        "PE",
    ):
        return {
            "Status": "INVALID",
            "Reasons": [
                "Option type must be CE or PE."
            ],
        }

    if option_data["Current Price"] <= 0:
        return {
            "Status": "INVALID",
            "Reasons": [
                "Option current price must be greater than zero."
            ],
        }

    if option_data["Volume"] < 0:
        return {
            "Status": "INVALID",
            "Reasons": [
                "Option volume cannot be negative."
            ],
        }

    # ---------------------------------------------------------
    # UNDERLYING VALIDATION
    # ---------------------------------------------------------

    for field in required_underlying_fields:

        value = underlying_data[field]

        if not isinstance(
            value,
            (int, float)
        ):
            return {
                "Status": "INVALID",
                "Reasons": [
                    f"Underlying {field} must be numeric."
                ],
            }

    if underlying_data["Current Price"] <= 0:
        return {
            "Status": "INVALID",
            "Reasons": [
                "Underlying current price must be greater than zero."
            ],
        }

    # ---------------------------------------------------------
    # OPTIONAL INPUT VALIDATION
    # ---------------------------------------------------------

    optional_values = {
        "Spread Percentage": spread_percentage,
        "Remaining Profit Percentage":
            remaining_profit_percentage,
        "Risk Reward Ratio": risk_reward_ratio,
    }

    for field, value in optional_values.items():

        if value is None:
            continue

        if not isinstance(
            value,
            (int, float)
        ):
            return {
                "Status": "INVALID",
                "Reasons": [
                    f"{field} must be numeric."
                ],
            }

    if spread_percentage is not None:
        if spread_percentage < 0:
            return {
                "Status": "INVALID",
                "Reasons": [
                    "Spread percentage cannot be negative."
                ],
            }

    if remaining_profit_percentage is not None:
        if remaining_profit_percentage < 0:
            return {
                "Status": "INVALID",
                "Reasons": [
                    "Remaining profit percentage "
                    "cannot be negative."
                ],
            }

    if risk_reward_ratio is not None:
        if risk_reward_ratio < 0:
            return {
                "Status": "INVALID",
                "Reasons": [
                    "Risk/reward ratio cannot be negative."
                ],
            }

    # ---------------------------------------------------------
    # UNDERLYING CONFIRMATION
    # ---------------------------------------------------------

    underlying_price = underlying_data[
        "Current Price"
    ]

    ma20 = underlying_data["MA20"]
    ma50 = underlying_data["MA50"]
    rsi = underlying_data["RSI"]

    if underlying_price > ma20 > ma50:
        trend_status = "BULLISH"
    elif underlying_price < ma20 < ma50:
        trend_status = "BEARISH"
    else:
        trend_status = "MIXED"

    # ---------------------------------------------------------
    # OPTION / UNDERLYING ALIGNMENT
    # ---------------------------------------------------------

    option_type = option_data["Option Type"]

    if option_type == "CE":

        if trend_status == "BULLISH":
            alignment = "SUPPORTIVE"
        elif trend_status == "BEARISH":
            alignment = "AGAINST"
        else:
            alignment = "MIXED"

    else:

        if trend_status == "BEARISH":
            alignment = "SUPPORTIVE"
        elif trend_status == "BULLISH":
            alignment = "AGAINST"
        else:
            alignment = "MIXED"

    # ---------------------------------------------------------
    # UNDERLYING MOMENTUM CONDITION
    # ---------------------------------------------------------

    if 45 <= rsi <= 70:
        underlying_momentum = "HEALTHY"
    elif rsi > 70:
        underlying_momentum = "OVEREXTENDED"
    elif rsi < 40:
        underlying_momentum = "WEAK"
    else:
        underlying_momentum = "MIXED"

    # ---------------------------------------------------------
    # ECONOMIC READINESS
    # ---------------------------------------------------------

    if (
        remaining_profit_percentage is not None
        and risk_reward_ratio is not None
    ):

        if (
            remaining_profit_percentage > 0
            and risk_reward_ratio >= 1.5
        ):
            economic_status = "VIABLE"
        else:
            economic_status = "NOT VIABLE"

    else:
        economic_status = "PENDING"

    # ---------------------------------------------------------
    # LIQUIDITY STATUS
    # ---------------------------------------------------------

    if spread_percentage is None:
        liquidity_status = "PENDING"

    elif spread_percentage <= 0.10:
        liquidity_status = "EXCELLENT"

    elif spread_percentage <= 0.25:
        liquidity_status = "GOOD"

    elif spread_percentage <= 0.50:
        liquidity_status = "ACCEPTABLE"

    else:
        liquidity_status = "POOR"

    # ---------------------------------------------------------
    # FINAL ENRICHED RECORD
    # ---------------------------------------------------------

    return {
        "Status": "READY",
        "Trading Symbol": option_data[
            "Trading Symbol"
        ],
        "Underlying": option_data[
            "Underlying"
        ],
        "Expiry": option_data[
            "Expiry"
        ],
        "Strike": option_data[
            "Strike"
        ],
        "Option Type": option_type,
        "Option Price": option_data[
            "Current Price"
        ],
        "Option Volume": option_data[
            "Volume"
        ],
        "Underlying Price": underlying_price,
        "Underlying MA20": ma20,
        "Underlying MA50": ma50,
        "Underlying RSI": rsi,
        "Underlying Trend": trend_status,
        "Option Alignment": alignment,
        "Underlying Momentum": underlying_momentum,
        "Spread Percentage": spread_percentage,
        "Liquidity Status": liquidity_status,
        "Remaining Profit Percentage":
            remaining_profit_percentage,
        "Risk Reward Ratio":
            risk_reward_ratio,
        "Economic Status": economic_status,
        "Reasons": [
            "Option candidate enriched with underlying "
            "confirmation and execution context."
        ],
    }