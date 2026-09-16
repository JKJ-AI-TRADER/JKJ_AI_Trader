"""
JKJ AI Trader
V12.2 — Real Market to V11 End-to-End Test

Purpose:
Test the complete path from a real Zerodha market quote
through V12.1 validation and V12.2 into a genuine V11
paper-trading position.

This test does NOT:
- place live orders
- create live broker positions
- make BUY decisions
- modify V1–V11
- modify main.py
"""

import os

from kiteconnect import KiteConnect

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)
from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.intraday_option_observation_record import (
    create_option_observation_record,
)

from modules.intraday_option_real_to_paper_bridge import (
    bridge_real_market_to_paper,
)

from modules.intraday_paper_trading import (
    open_paper_trade,
)





def main():
    print("\nJKJ AI Trader — V12.2 Real Market → V11 Paper Test")
    print("=" * 60)

    api_key = os.environ.get("JKJ_KITE_API_KEY")

    if not api_key:
        print("ERROR: JKJ_KITE_API_KEY is not available.")
        return

    api_secret = os.environ.get("JKJ_KITE_API_SECRET")

    if not api_secret:
        print("ERROR: JKJ_KITE_API_SECRET is not available.")
        return

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
        print("ERROR: NIFTY option contract selection failed.")
        print(contracts)
        return

    contract = contracts["Contracts"][0]

    TRADING_SYMBOL = contract.get("tradingsymbol")
    INSTRUMENT_TOKEN = contract.get("instrument_token")
    STRIKE = contract.get("strike")
    OPTION_TYPE = contract.get("instrument_type")
    EXPIRY = contract.get("expiry")

    print("\nDynamic NIFTY contract selected:")
    print("Trading Symbol:", TRADING_SYMBOL)
    print("Instrument Token:", INSTRUMENT_TOKEN)
    print("Strike:", STRIKE)
    print("Option Type:", OPTION_TYPE)
    print("Expiry:", EXPIRY)
    quote_response = kite.quote(
        [
            f"NFO:{TRADING_SYMBOL}",
            "NSE:NIFTY 50",
        ]
    )

    print("Fresh Zerodha quote received.")

    underlying_price = quote_response[
        "NSE:NIFTY 50"
    ].get("last_price")

    underlying_data = {
        "Underlying": "NIFTY",
        "Current Price": underlying_price,
    }

    adapted_data = adapt_zerodha_option_quote(
        quote_response,
        TRADING_SYMBOL,
        INSTRUMENT_TOKEN,
    )

    print("\n1. Adapter:")
    print(adapted_data)

    observed_data = observe_option_market(
        adapted_data,
        underlying_data,
    )

    print("\n2. Observer:")
    print(observed_data)

    if observed_data.get("Status") != "READY":
        print("\nEND-TO-END TEST STOPPED: Observation not READY.")
        return

    record = create_option_observation_record(
        observed_data
    )

    print("\n3. Observation Record:")
    print(record)

    if record.get("Status") != "RECORDED":
        print("\nEND-TO-END TEST STOPPED: Record not created.")
        return

    paper_trade = open_paper_trade(
        trade_id="V12-2-REAL-MARKET-E2E",
        symbol=TRADING_SYMBOL,
        instrument_type="OPTION",
        entry_price=1600.00,
        quantity=65,
        stop_loss=1550.00,
        target=1700.00,
        underlying="NIFTY",
        expiry=EXPIRY,
        strike=STRIKE,
        option_type=OPTION_TYPE,
    )

    print("\n4. V11 Paper Trade:")
    print(paper_trade)

    bridge_result = bridge_real_market_to_paper(
        record,
        paper_trade,
    )

    print("\n5. V12.2 Bridge:")
    print(bridge_result)

    if bridge_result.get("Status") != "BRIDGED":
        print("\nEND-TO-END TEST: FAILED")
        return

    updated_trade = bridge_result.get(
        "Paper Trade",
        {}
    )

    print("\n6. Final V11 Paper Position:")
    print(updated_trade)

    assert updated_trade.get("Status") == "OPEN"
    assert updated_trade.get("Entry Price") == 1600.00
    assert updated_trade.get("Current Price") == record.get(
        "Current Price"
    )
    assert updated_trade.get("Current Quantity") == 65
    assert updated_trade.get("Original Quantity") == 65

    print("\n" + "=" * 60)
    print("V12.2 REAL MARKET → V11 PAPER END-TO-END: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()