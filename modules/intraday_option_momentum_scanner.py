"""
JKJ AI Trader
Intraday Option Momentum Scanner V5

Purpose:
Evaluate multiple NIFTY option histories using the existing
Intraday Momentum Engine and rank the opportunities.

This module does NOT:
- place orders
- connect to Zerodha
- make BUY/SELL decisions
- modify main.py
- modify the existing Momentum Engine
"""

from intraday_momentum_engine import (
    analyse_intraday_momentum
)


def scan_option_momentum(
    option_histories,
    option_context=None,
):
    """
    Scan multiple option histories and rank them by momentum score.

    Parameters
    ----------
    option_histories : dict
        Dictionary in the form:

        {
            "TRADING_SYMBOL": pandas.DataFrame,
            ...
        }

    option_context : dict, optional
        Optional additional information for each option.

    Returns
    -------
    dict
        Ranked option momentum results.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not isinstance(option_histories, dict):
        return {
            "Status": "INVALID",
            "Ranked Opportunities": [],
            "Reasons": [
                "Option histories must be a dictionary."
            ],
        }

    if len(option_histories) == 0:
        return {
            "Status": "INVALID",
            "Ranked Opportunities": [],
            "Reasons": [
                "At least one option history is required."
            ],
        }

    if option_context is not None and not isinstance(
        option_context,
        dict
    ):
        return {
            "Status": "INVALID",
            "Ranked Opportunities": [],
            "Reasons": [
                "Option context must be a dictionary."
            ],
        }

    # ---------------------------------------------------------
    # SCAN
    # ---------------------------------------------------------

    results = []

    for trading_symbol, history in option_histories.items():

        if not trading_symbol:
            continue

        momentum_result = analyse_intraday_momentum(
            history
        )

        context = {}

        if option_context is not None:
            context = option_context.get(
                trading_symbol,
                {}
            )

        if not isinstance(context, dict):
            context = {}

        result = {
            "Trading Symbol": trading_symbol,
            "Underlying": context.get(
                "Underlying",
                "NIFTY"
            ),
            "Expiry": context.get(
                "Expiry"
            ),
            "Strike": context.get(
                "Strike"
            ),
            "Option Type": context.get(
                "Option Type"
            ),
            "Momentum Score": momentum_result.get(
                "Momentum Score",
                0
            ),
            "Momentum Status": momentum_result.get(
                "Momentum Status",
                "NO TRADE"
            ),
            "Trade Candidate": momentum_result.get(
                "Trade Candidate",
                False
            ),
            "Exhaustion Score": momentum_result.get(
                "Exhaustion Penalty",
                0
            ),
            "Reasons": momentum_result.get(
                "Reasons",
                []
            ),
            "Warnings": momentum_result.get(
                "Warnings",
                []
            ),
        }

        results.append(result)

    # ---------------------------------------------------------
    # RANK
    # ---------------------------------------------------------

    results.sort(
        key=lambda item: item["Momentum Score"],
        reverse=True
    )

    for rank, result in enumerate(
        results,
        start=1
    ):
        result["Rank"] = rank

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    if len(results) == 0:
        status = "NO RESULTS"
    else:
        status = "READY"

    return {
        "Status": status,
        "Scanned Count": len(option_histories),
        "Result Count": len(results),
        "Ranked Opportunities": results,
        "Reasons": [
            "Options scanned and ranked using the existing "
            "Intraday Momentum Engine."
        ],
    }