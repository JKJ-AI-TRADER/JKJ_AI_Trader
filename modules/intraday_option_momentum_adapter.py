"""
JKJ AI Trader
Intraday Option Momentum Adapter V4

Purpose:
Convert standardized option market data into the OHLCV structure
required by the existing Intraday Momentum Engine.

This module does NOT:
- place orders
- connect to Zerodha
- modify the Momentum Engine
- make BUY/SELL decisions
"""

import pandas as pd


def prepare_option_momentum_data(
    option_history
):
    """
    Prepare option historical data for the existing
    intraday momentum engine.

    Expected input columns:
        Open
        High
        Low
        Close
        Volume

    Returns:
        pandas DataFrame suitable for
        analyse_intraday_momentum()
    """

    if option_history is None:
        return {
            "Status": "INVALID",
            "Reasons": ["Option history is required."]
        }

    if not isinstance(option_history, pd.DataFrame):
        return {
            "Status": "INVALID",
            "Reasons": ["Option history must be a pandas DataFrame."]
        }

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in option_history.columns
    ]

    if missing_columns:
        return {
            "Status": "INVALID",
            "Reasons": [
                f"Missing required columns: {missing_columns}"
            ]
        }

    if len(option_history) < 20:
        return {
            "Status": "INVALID",
            "Reasons": [
                "At least 20 option history bars are required."
            ]
        }

    momentum_data = option_history[
        required_columns
    ].copy()

    for column in required_columns:

        momentum_data[column] = pd.to_numeric(
            momentum_data[column],
            errors="coerce"
        )

    if momentum_data[required_columns].isnull().any().any():
        return {
            "Status": "INVALID",
            "Reasons": [
                "Option history contains invalid numeric values."
            ]
        }

    if (momentum_data["Close"] <= 0).any():
        return {
            "Status": "INVALID",
            "Reasons": [
                "Close prices must be greater than zero."
            ]
        }

    if (momentum_data["Volume"] < 0).any():
        return {
            "Status": "INVALID",
            "Reasons": [
                "Volume cannot be negative."
            ]
        }

    momentum_data = momentum_data.reset_index(
        drop=True
    )

    return {
        "Status": "READY",
        "Data Status": "VALID",
        "Bars": len(momentum_data),
        "Columns": required_columns,
        "Momentum Data": momentum_data,
        "Reasons": [
            "Option history prepared for the existing "
            "Intraday Momentum Engine."
        ]
    }