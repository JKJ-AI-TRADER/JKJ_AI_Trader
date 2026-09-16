"""
JKJ AI Trader
Test — NIFTY Option Contract Selector

Purpose:
Validate dynamic NIFTY option contract selection
using the live Zerodha session and NFO instrument list.

This test does NOT:
- place orders
- modify main.py
- write market observations
- make trading decisions
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)


result = get_kite_session()

print(
    "SESSION STATUS:",
    result.get("Status")
)

if result.get("Kite"):

    kite = result["Kite"]

    instruments = kite.instruments(
        "NFO"
    )

    nifty_spot = kite.ltp(
        "NSE:NIFTY 50"
    )["NSE:NIFTY 50"]["last_price"]

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

        print(
            "NO NIFTY EXPIRY FOUND"
        )

    else:

        selected_expiry = expiries[0]

        selection = select_nearby_contracts(
            instruments=nifty_options,
            nifty_spot=nifty_spot,
            expiry=selected_expiry,
            contracts_per_side=2,
        )

        print(
            "SELECTION STATUS:",
            selection.get("Status")
        )

        print(
            "NIFTY SPOT:",
            selection.get("NIFTY Spot")
        )

        print(
            "EXPIRY:",
            selection.get("Expiry")
        )

        for contract in selection.get(
            "Contracts",
            [],
        ):

            print(
                contract.get(
                    "tradingsymbol"
                ),
                "|",
                contract.get(
                    "instrument_type"
                ),
                "| STRIKE:",
                contract.get(
                    "strike"
                ),
                "| TOKEN:",
                contract.get(
                    "instrument_token"
                ),
            )