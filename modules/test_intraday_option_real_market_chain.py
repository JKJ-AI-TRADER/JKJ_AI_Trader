"""
JKJ AI Trader
V12.1 — Full Real-Market Observation Chain Test

Purpose:
Test the complete V12.1 observation flow using a real
Zerodha quote.

Flow:
Zerodha Quote
    ↓
Zerodha Option Adapter
    ↓
Real-Market Observer
    ↓
Observation Record

This test does NOT:
- place orders
- make BUY/SELL decisions
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

from modules.intraday_option_observation_record import (
    create_option_observation_record,
)


TRADING_SYMBOL = "NIFTY2691525000PE"
INSTRUMENT_TOKEN = 12125186


def main():
    print("\nJKJ AI Trader — V12.1 Full Real-Market Chain Test")
    print("=" * 55)

    api_key = os.environ.get("JKJ_KITE_API_KEY")

    if not api_key:
        print("ERROR: JKJ_KITE_API_KEY is not available.")
        return

    kite = KiteConnect(api_key=api_key)

    print("\nPlease authenticate with a fresh Zerodha session.")
    print("Paste the fresh callback URL below.")

    login_url = kite.login_url()

    print("\nKite Login URL:")
    print(login_url)

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

    api_secret = os.environ.get("JKJ_KITE_API_SECRET")

    if not api_secret:
        print("ERROR: JKJ_KITE_API_SECRET is not available.")
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

    print("\nAdapter Result:")
    print(adapted_data)

    observed_data = observe_option_market(
        adapted_data,
        underlying_data,
    )

    print("\nObserver Result:")
    print(observed_data)

    if observed_data.get("Status") != "READY":
        print("\nCHAIN TEST STOPPED: Observation not READY.")
        return

    record = create_option_observation_record(
        observed_data
    )

    print("\nObservation Record:")
    print(record)

    if record.get("Status") == "RECORDED":
        print("\n" + "=" * 55)
        print("V12.1 FULL REAL-MARKET CHAIN: PASS")
        print("=" * 55)
    else:
        print("\nV12.1 FULL REAL-MARKET CHAIN: FAILED")


if __name__ == "__main__":
    main()