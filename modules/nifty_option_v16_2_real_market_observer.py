"""
JKJ AI Trader
V16.2 Stage 1 — Real-Market Option Observation

Purpose:
Collect one fresh NIFTY option observation from Zerodha
using the existing V12.1 observation architecture.

This module does NOT:
- place live orders
- make BUY/SELL decisions
- calculate momentum
- calculate opportunity scores
- create paper trades
- modify V12.1 modules
- modify V13-V15 modules
- modify main.py
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)

from modules.intraday_option_observation_record import (
    create_option_observation_record,
)


def collect_real_market_observation(
    option_type="CE",
):
    """
    Collect one fresh, validated NIFTY option observation.

    Returns a RECORDED observation when successful.
    """

    session_result = get_kite_session()

    if session_result.get("Kite") is None:
        return {
            "Status": "REJECTED",
            "Stage": "SESSION",
            "Reason": session_result.get(
                "Reason",
                "Zerodha session unavailable.",
            ),
        }

    kite = session_result["Kite"]

    instruments = kite.instruments("NFO")

    if not isinstance(instruments, list):
        return {
            "Status": "REJECTED",
            "Stage": "INSTRUMENTS",
            "Reason": "NFO instrument list unavailable.",
        }

    nifty_spot = kite.ltp(
        "NSE:NIFTY 50"
    )["NSE:NIFTY 50"]["last_price"]

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        return {
            "Status": "REJECTED",
            "Stage": "NIFTY",
            "Reason": "Invalid NIFTY spot price.",
        }

    nifty_options = [
        item
        for item in instruments
        if item.get("name") == "NIFTY"
        and item.get("instrument_type") in (
            "CE",
            "PE",
        )
    ]

    expiries = sorted({
        item.get("expiry")
        for item in nifty_options
        if item.get("expiry")
    })

    if not expiries:
        return {
            "Status": "REJECTED",
            "Stage": "EXPIRY",
            "Reason": "No NIFTY option expiry found.",
        }

    selected_expiry = expiries[0]

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=2,
    )

    if selection.get("Status") != "SELECTED":
        return {
            "Status": "REJECTED",
            "Stage": "CONTRACT_SELECTION",
            "Reason": selection.get(
                "Reason",
                "NIFTY option contract selection failed.",
            ),
        }

    contracts = [
        contract
        for contract in selection.get(
            "Contracts",
            [],
        )
        if contract.get("instrument_type") == option_type
    ]

    if not contracts:
        return {
            "Status": "REJECTED",
            "Stage": "CONTRACT_SELECTION",
            "Reason": (
                f"No {option_type} contract was selected."
            ),
        }

    contract = contracts[0]

    trading_symbol = contract.get(
        "tradingsymbol"
    )

    instrument_token = contract.get(
        "instrument_token"
    )

    if not trading_symbol or not instrument_token:
        return {
            "Status": "REJECTED",
            "Stage": "CONTRACT_SELECTION",
            "Reason": "Selected contract is incomplete.",
        }

    quote_response = kite.quote(
        [
            f"NFO:{trading_symbol}",
            "NSE:NIFTY 50",
        ]
    )

    underlying_price = quote_response[
        "NSE:NIFTY 50"
    ].get("last_price")

    underlying_data = {
        "Underlying": "NIFTY",
        "Current Price": underlying_price,
    }

    adapted_data = adapt_zerodha_option_quote(
        quote_response,
        trading_symbol,
        instrument_token,
    )

   
    observed_data = observe_option_market(
        adapted_data,
        underlying_data,
    )

    if observed_data.get("Status") != "READY":
        return {
            "Status": "REJECTED",
            "Stage": "OBSERVER",
            "Reason": observed_data.get(
                "Reasons",
                ["Real-market observation was not READY."],
            ),
            "Observer Result": observed_data,
        }

    record = create_option_observation_record(
        observed_data
    )

    if record.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Stage": "OBSERVATION_RECORD",
            "Reason": record.get(
                "Reason",
                "Observation record was not created.",
            ),
            "Observation Result": record,
        }

    return {
        "Status": "RECORDED",
        "Stage": "V16.2_STAGE_1",
        "Session Status": session_result.get(
            "Status"
        ),
        "NIFTY Spot": nifty_spot,
        "Expiry": selected_expiry,
        "Trading Symbol": trading_symbol,
        "Option Type": option_type,
        "Instrument Token": instrument_token,
        "Observation": record,
    }
