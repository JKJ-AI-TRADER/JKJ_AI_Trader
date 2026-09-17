"""
JKJ AI Trader
V12.3 — Real Market → Movement Recorder → Storage Test

Purpose:
Verify that a real Zerodha NIFTY option observation can flow through:

Zerodha
    ↓
Dynamic Contract Selection
    ↓
V12.1 Observer
    ↓
V12.3 Movement Recorder
    ↓
V12.3 Observation Storage

This test does NOT:
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify main.py
- modify V1–V11
"""

import os

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)

from modules.nifty_option_movement_recorder import (
    record_option_observation,
)

import modules.nifty_option_observation_storage as storage




def main():

    print(
        "\nJKJ AI Trader — "
        "V12.3 Real Market → Movement → Storage Test"
    )
    print("=" * 70)

    api_key = os.environ.get("JKJ_KITE_API_KEY")

    if not api_key:
        print("ERROR: JKJ_KITE_API_KEY is not available.")
        return

    api_secret = os.environ.get("JKJ_KITE_API_SECRET")

    if not api_secret:
        print("ERROR: JKJ_KITE_API_SECRET is not available.")
        return

    from kiteconnect import KiteConnect

    kite = KiteConnect(api_key=api_key)

    print("\nPlease authenticate with a fresh Zerodha session.")

    print("\nKite Login URL:")
    print(kite.login_url())

    callback_url = input(
        "\nPaste fresh callback URL: "
    ).strip()

    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(callback_url)
    query_params = parse_qs(parsed_url.query)

    request_token = query_params.get(
        "request_token",
        [None]
    )[0]

    if not request_token:
        print("ERROR: Request token was not found.")
        return

    session_data = kite.generate_session(
        request_token,
        api_secret=api_secret,
    )

    access_token = session_data.get("access_token")

    if not access_token:
        print("ERROR: Access token was not generated.")
        return

    kite.set_access_token(access_token)

    print("\nZerodha authentication: SUCCESS")

    # ---------------------------------------------------------
    # 1. Dynamic NIFTY contract selection
    # ---------------------------------------------------------

    nfo_instruments = kite.instruments("NFO")

    nifty_ltp = kite.ltp("NSE:NIFTY 50")
    nifty_spot = nifty_ltp["NSE:NIFTY 50"]["last_price"]

    nifty_options = [
        item
        for item in nfo_instruments
        if item.get("name") == "NIFTY"
        and item.get("instrument_type") in ("CE", "PE")
    ]

    expiries = sorted(
        {
            item.get("expiry")
            for item in nifty_options
            if item.get("expiry") is not None
        }
    )

    selected_expiry = expiries[0]

    contracts = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=1,
    )

    if contracts.get("Status") != "SELECTED":
        print("\nERROR: Contract selection failed.")
        print(contracts)
        return

    contract = contracts["Contracts"][0]

    trading_symbol = contract.get("tradingsymbol")
    instrument_token = contract.get("instrument_token")
    strike = contract.get("strike")
    option_type = contract.get("instrument_type")
    expiry = contract.get("expiry")

    print("\nDynamic NIFTY contract selected:")
    print("Trading Symbol:", trading_symbol)
    print("Instrument Token:", instrument_token)
    print("Strike:", strike)
    print("Option Type:", option_type)
    print("Expiry:", expiry)

    # ---------------------------------------------------------
    # 2. Fresh Zerodha quote
    # ---------------------------------------------------------

    quote_response = kite.quote(
        [
            f"NFO:{trading_symbol}",
            "NSE:NIFTY 50",
        ]
    )

    option_quote = quote_response.get(
        f"NFO:{trading_symbol}"
    )

    nifty_quote = quote_response.get(
        "NSE:NIFTY 50"
    )

    print("\nFresh Zerodha quote received.")

    # ---------------------------------------------------------
    # 3. V12.1 Adapter
    # ---------------------------------------------------------

    adapted = adapt_zerodha_option_quote(
        quote_response=quote_response,
        trading_symbol=trading_symbol,
        instrument_token=instrument_token,
        underlying="NIFTY",
    )

    print("\n1. Adapter:")
    print(adapted)

    if not isinstance(adapted, dict):
        print("\nTEST STOPPED: Adapter returned invalid data.")
        return

    # ---------------------------------------------------------
    # 4. V12.1 Observer
    # ---------------------------------------------------------

    observation = observe_option_market(
    adapted
    )

    print("\n2. Observer:")
    print(observation)

    if observation.get("Status") != "READY":
        print("\nTEST STOPPED: Observation not READY.")
        return

    # ---------------------------------------------------------
    # 5. V12.3 Movement Recorder
    # ---------------------------------------------------------

    expiry_string = str(expiry)

    movement_record = record_option_observation(
        trading_symbol=trading_symbol,
        underlying="NIFTY",
        expiry=expiry_string,
        strike=strike,
        option_type=option_type,
        current_price=observation.get(
            "Current Price"
        ),
        volume=observation.get(
            "Volume"
        ),
        open_interest=observation.get(
            "Open Interest"
        ),
        nifty_spot_price=nifty_spot,
        timestamp=observation.get(
            "Observation Timestamp"
        ),
    )

    print("\n3. V12.3 Movement Record:")
    print(movement_record)

    if movement_record.get("Status") != "RECORDED":
        print("\nTEST STOPPED: Movement record failed.")
        return

    # ---------------------------------------------------------
    # 6. V12.3 Observation Storage
    # ---------------------------------------------------------

    storage_result = storage.save_option_observation(
        movement_record
    )

    print("\n4. V12.3 Storage:")
    print(storage_result)

    if storage_result.get("Status") != "SAVED":
        print("\nTEST STOPPED: Storage failed.")
        return

    # ---------------------------------------------------------
    # 7. Verify file exists
    # ---------------------------------------------------------

    if not os.path.isfile(
        storage.OBSERVATION_FILE
    ):
        print("\nTEST FAILED: CSV file not created.")
        return

    print("\nCSV file created successfully.")

    # ---------------------------------------------------------
    # 8. Cleanup test file
    # ---------------------------------------------------------

    os.remove(
        storage.OBSERVATION_FILE
    )

    print("Test CSV cleaned up.")

    print("\n" + "=" * 70)
    print(
        "V12.3 REAL MARKET → MOVEMENT → STORAGE: PASS"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()