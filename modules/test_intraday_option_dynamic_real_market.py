"""
JKJ AI Trader
V12.1 — Dynamic Real-Market Option Observation Test

Purpose:
Test the complete real-market observation flow using
dynamically selected NIFTY option contracts.

Flow:

Existing Zerodha Session
        ↓
NFO Instrument List
        ↓
Dynamic NIFTY Contract Selector
        ↓
Selected CE / PE Contracts
        ↓
Zerodha Quote
        ↓
Zerodha Option Adapter
        ↓
Option Market Data Provider V3
        ↓
Real-Market Observer
        ↓
Observation Result

This test does NOT:
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify V1–V11
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

from modules.intraday_option_market_data import (
    create_option_market_data,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)


def main():

    print()
    print("=" * 60)
    print("JKJ AI TRADER — DYNAMIC REAL-MARKET OPTION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # STEP 1 — EXISTING ZERODHA SESSION
    # ---------------------------------------------------------

    print()
    print("STEP 1 — ZERODHA SESSION")
    print("-" * 60)

    session_result = get_kite_session()

    print(
        "SESSION STATUS:",
        session_result.get("Status")
    )

    if not session_result.get("Kite"):

        print(
            "TEST STOPPED: Zerodha session unavailable."
        )

        return

    kite = session_result["Kite"]

    # ---------------------------------------------------------
    # STEP 2 — NFO INSTRUMENTS
    # ---------------------------------------------------------

    print()
    print("STEP 2 — NFO INSTRUMENT LIST")
    print("-" * 60)

    instruments = kite.instruments("NFO")

    print(
        "NFO INSTRUMENTS:",
        len(instruments)
    )

    if not instruments:

        print(
            "TEST STOPPED: NFO instrument list is empty."
        )

        return

    # ---------------------------------------------------------
    # STEP 3 — NIFTY SPOT
    # ---------------------------------------------------------

    print()
    print("STEP 3 — NIFTY SPOT")
    print("-" * 60)

    nifty_quote = kite.ltp(
        "NSE:NIFTY 50"
    )

    nifty_spot = nifty_quote[
        "NSE:NIFTY 50"
    ]["last_price"]

    print(
        "NIFTY SPOT:",
        nifty_spot
    )

    if not isinstance(
        nifty_spot,
        (int, float)
    ):

        print(
            "TEST STOPPED: NIFTY spot is invalid."
        )

        return

    # ---------------------------------------------------------
    # STEP 4 — FILTER NIFTY OPTIONS
    # ---------------------------------------------------------

    print()
    print("STEP 4 — NIFTY OPTION UNIVERSE")
    print("-" * 60)

    nifty_options = [
        item
        for item in instruments
        if item.get("name") == "NIFTY"
        and item.get("instrument_type") in (
            "CE",
            "PE",
        )
    ]

    print(
        "NIFTY OPTION CONTRACTS:",
        len(nifty_options)
    )

    if not nifty_options:

        print(
            "TEST STOPPED: No NIFTY option contracts found."
        )

        return

    # ---------------------------------------------------------
    # STEP 5 — FIND AVAILABLE EXPIRY
    # ---------------------------------------------------------

    print()
    print("STEP 5 — SELECT EXPIRY")
    print("-" * 60)

    expiries = sorted({
        item.get("expiry")
        for item in nifty_options
        if item.get("expiry")
    })

    if not expiries:

        print(
            "TEST STOPPED: No NIFTY expiry found."
        )

        return

    selected_expiry = expiries[0]

    print(
        "SELECTED EXPIRY:",
        selected_expiry
    )

    # ---------------------------------------------------------
    # STEP 6 — DYNAMIC CONTRACT SELECTION
    # ---------------------------------------------------------

    print()
    print("STEP 6 — DYNAMIC CONTRACT SELECTION")
    print("-" * 60)

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=1,
    )

    print(
        "SELECTION STATUS:",
        selection.get("Status")
    )

    if selection.get("Status") != "SELECTED":

        print(
            "TEST STOPPED:",
            selection.get("Reason")
        )

        return

    contracts = selection.get(
        "Contracts",
        []
    )

    if not contracts:

        print(
            "TEST STOPPED: No contracts selected."
        )

        return

    for contract in contracts:

        print(
            contract.get("tradingsymbol"),
            "|",
            contract.get("instrument_type"),
            "| STRIKE:",
            contract.get("strike"),
            "| TOKEN:",
            contract.get("instrument_token"),
        )

    # ---------------------------------------------------------
    # STEP 7 — QUOTE SELECTED CONTRACTS
    # ---------------------------------------------------------

    print()
    print("STEP 7 — ZERODHA LIVE QUOTE")
    print("-" * 60)

    quote_symbols = [
        f"NFO:{contract.get('tradingsymbol')}"
        for contract in contracts
    ]

    quote_symbols.append(
        "NSE:NIFTY 50"
    )

    quote_response = kite.quote(
        quote_symbols
    )
    print()
    print("RAW ZERODHA OPTION QUOTE:")
    print("-" * 60)

    for symbol in quote_symbols:
        if symbol.startswith("NFO:"):
            print(symbol)
            print(quote_response.get(symbol))
            print()
    print(
        "QUOTE RECEIVED:",
        len(quote_response)
    )

    # ---------------------------------------------------------
    # STEP 8 — PROCESS EACH CONTRACT
    # ---------------------------------------------------------

    print()
    print("STEP 8 — OPTION OBSERVATIONS")
    print("-" * 60)

    successful_observations = 0

    for contract in contracts:

        trading_symbol = contract.get(
            "tradingsymbol"
        )

        instrument_token = contract.get(
            "instrument_token"
        )

        strike = contract.get(
            "strike"
        )

        option_type = contract.get(
            "instrument_type"
        )

        expiry = contract.get(
            "expiry"
        )

        # -----------------------------------------------------
        # ADAPTER
        # -----------------------------------------------------

        adapted_data = adapt_zerodha_option_quote(
            quote_response,
            trading_symbol,
            instrument_token,
        )

        print()
        print(
            "CONTRACT:",
            trading_symbol
        )

        print(
            "ADAPTER STATUS:",
            adapted_data.get("Status")
        )

        # -----------------------------------------------------
        # BUILD STANDARDIZED MARKET DATA
        # -----------------------------------------------------

        market_data = create_option_market_data(

            trading_symbol=trading_symbol,

            instrument_token=instrument_token,

            underlying="NIFTY",

            expiry=expiry,

            strike=strike,

            option_type=option_type,

            current_price=adapted_data.get(
                "Current Price"
            ),

            open_price=adapted_data.get(
                "Open"
            ),

            high_price=adapted_data.get(
                "High"
            ),

            low_price=adapted_data.get(
                "Low"
            ),

            volume=adapted_data.get(
                "Volume"
            ),

            timestamp=adapted_data.get(
                "Last Trade Time"
            ),
        )

        print(
            "MARKET DATA STATUS:",
            market_data.get("Status")
        )

        if market_data.get("Status") != "READY":

            print(
                "MARKET DATA REASON:",
                market_data.get("Reasons")
            )

            continue

        # -----------------------------------------------------
        # OBSERVER
        # -----------------------------------------------------

        underlying_data = {
            "Underlying": "NIFTY",
            "Current Price": nifty_spot,
        }

        observed_data = observe_option_market(
            market_data,
            underlying_data,
        )

        print(
            "OBSERVER STATUS:",
            observed_data.get("Status")
        )

        if observed_data.get("Status") == "READY":

            successful_observations += 1

            print(
                "CURRENT PRICE:",
                observed_data.get(
                    "Current Price"
                )
            )

            print(
                "VOLUME:",
                observed_data.get(
                    "Volume"
                )
            )

            print(
                "LAST TRADE TIME:",
                observed_data.get(
                    "Last Trade Time"
                )
            )

        else:

            print(
                "OBSERVER REASON:",
                observed_data.get("Reasons")
            )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print()
    print("=" * 60)

    if successful_observations == len(contracts):

        print(
            "V12.1 DYNAMIC REAL-MARKET OPTION TEST: PASS"
        )

    else:

        print(
            "V12.1 DYNAMIC REAL-MARKET OPTION TEST: FAILED"
        )

        print(
            "Successful observations:",
            successful_observations,
            "/",
            len(contracts)
        )

    print("=" * 60)


if __name__ == "__main__":
    main()