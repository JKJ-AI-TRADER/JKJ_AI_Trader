"""
JKJ AI Trader
V21.2.7 — Real-Market Observation Cycle

Purpose:
Capture one fresh observation for each contract in the
validated V21.2 observation universe.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- create opportunity scores
- modify V12.1-V21.1 modules
- modify main.py

Observation chain:

Zerodha Quote
    ↓
V12.1 Option Adapter
    ↓
V12.1 Real-Market Observer
    ↓
Observation Record
"""

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)

from modules.intraday_option_observation_record import (
    create_option_observation_record,
)


def capture_candidate_observation(
    kite,
    contract,
):
    """
    Capture one fresh observation for one locked contract.
    """

    if kite is None:
        return {
            "Status": "REJECTED",
            "Reason": "Kite session is required.",
        }

    if not isinstance(contract, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Contract must be a dictionary.",
        }

    required_fields = (
        "tradingsymbol",
        "instrument_token",
        "expiry",
        "strike",
        "instrument_type",
    )

    missing_fields = [
        field
        for field in required_fields
        if contract.get(field) is None
    ]

    if missing_fields:
        return {
            "Status": "REJECTED",
            "Reason": (
                "Contract identity incomplete: "
                f"{missing_fields}"
            ),
        }

    trading_symbol = contract["tradingsymbol"]
    instrument_token = contract["instrument_token"]

    try:

        quote_response = kite.quote(
            [
                f"NFO:{trading_symbol}",
                "NSE:NIFTY 50",
            ]
        )

    except Exception as error:

        return {
            "Status": "REJECTED",
            "Reason": f"Zerodha quote failed: {error}",
            "Trading Symbol": trading_symbol,
        }

    if not isinstance(quote_response, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid Zerodha quote response.",
            "Trading Symbol": trading_symbol,
        }

    nifty_quote = quote_response.get(
        "NSE:NIFTY 50"
    )

    if not isinstance(nifty_quote, dict):
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY quote missing.",
            "Trading Symbol": trading_symbol,
        }

    nifty_spot = nifty_quote.get(
        "last_price"
    )

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Invalid NIFTY spot price.",
            "Trading Symbol": trading_symbol,
        }

    # -----------------------------------------------
    # V12.1 — OPTION ADAPTER
    # -----------------------------------------------

    adapted_data = adapt_zerodha_option_quote(
        quote_response,
        trading_symbol,
        instrument_token,
    )

    if not isinstance(adapted_data, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Option quote adapter returned invalid data.",
            "Trading Symbol": trading_symbol,
        }

    # -----------------------------------------------
    # V12.1 — REAL-MARKET OBSERVER
    # -----------------------------------------------

    underlying_data = {
        "Underlying": "NIFTY",
        "Current Price": nifty_spot,
    }

    observed_data = observe_option_market(
        adapted_data,
        underlying_data,
    )

    if observed_data.get("Status") != "READY":
        return {
            "Status": "REJECTED",
            "Reason": observed_data.get(
                "Reasons",
                ["Real-market observation was not READY."],
            ),
            "Trading Symbol": trading_symbol,
        }

    # -----------------------------------------------
    # V12.1 — OBSERVATION RECORD
    # -----------------------------------------------

    record = create_option_observation_record(
        observed_data
    )

    if record.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": record.get(
                "Reasons",
                ["Observation record was not created."],
            ),
            "Trading Symbol": trading_symbol,
        }

    # -----------------------------------------------
    # JKJ CONTRACT CONTEXT
    # -----------------------------------------------

    record["NIFTY Spot Price"] = nifty_spot
    record["Expiry"] = contract["expiry"]
    record["Strike"] = contract["strike"]
    record["Option Type"] = contract["instrument_type"]
    record["Timestamp"] = record.get(
        "Observation Timestamp"
    )

    return record


def capture_observation_cycle(
    kite,
    contracts,
):
    """
    Capture one observation cycle across all prepared
    NIFTY CE/PE candidates.
    """

    if kite is None:
        return {
            "Status": "REJECTED",
            "Reason": "Kite session is required.",
        }

    if not isinstance(contracts, list):
        return {
            "Status": "REJECTED",
            "Reason": "Contracts must be a list.",
        }

    if not contracts:
        return {
            "Status": "REJECTED",
            "Reason": "Observation contract list is empty.",
        }

    observations = []

    for contract in contracts:

        observation = capture_candidate_observation(
            kite,
            contract,
        )

        if observation.get("Status") != "RECORDED":

            return {
                "Status": "REJECTED",
                "Reason": observation.get(
                    "Reason",
                    "Candidate observation failed.",
                ),
                "Completed Observations": len(
                    observations
                ),
            }

        observations.append(
            observation
        )

    return {
        "Status": "OBSERVATION_CYCLE_COMPLETE",
        "Observation Count": len(observations),
        "Observations": observations,
        "Live Order": False,
        "Paper Trade": False,
    }
