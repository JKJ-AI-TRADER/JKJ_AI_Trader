"""
JKJ AI Trader
V12.3 — Real Market → V11 Paper → V10 Monitor

Purpose:
Test the complete real-market observation path into the
existing V10 option paper position monitor.

Architecture:
Zerodha
→ V12.1 Adapter
→ V12.1 Observer
→ V12.1 Observation Record
→ V11 Paper Position
→ V12.2 Bridge
→ V12.3 Monitor Bridge
→ V10 Monitor

Safety:
- Real market DATA ONLY
- No live orders
- No paper exit execution
- No main.py changes
"""

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

from modules.intraday_option_real_to_paper_bridge import (
    bridge_real_market_to_paper,
)

from modules.intraday_option_paper_monitor_bridge import (
    monitor_real_market_paper_position,
)

from modules.intraday_paper_trading import (
    open_paper_trade,
)


TRADING_SYMBOL = "NIFTY2691525000PE"
INSTRUMENT_TOKEN = 12125186
UNDERLYING = "NIFTY"


def authenticate_zerodha():
    api_key = __import__("os").getenv("JKJ_KITE_API_KEY")
    api_secret = __import__("os").getenv("JKJ_KITE_API_SECRET")

    if not api_key or not api_secret:
        raise RuntimeError(
            "JKJ_KITE_API_KEY or JKJ_KITE_API_SECRET is not available."
        )

    kite = KiteConnect(api_key=api_key)

    login_url = kite.login_url()

    print("\nOpen this Zerodha login URL in your browser:")
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

    session_data = kite.generate_session(
        request_token,
        api_secret=api_secret,
    )

    kite.set_access_token(session_data["access_token"])

    print("Zerodha authentication: PASS")

    return kite


def main():
    print("\nJKJ AI Trader — V12.3 Real Market → V10")
    print("=" * 65)

    # ---------------------------------------------------------
    # STEP 1 — Zerodha authentication
    # ---------------------------------------------------------

    kite = authenticate_zerodha()

    # ---------------------------------------------------------
    # STEP 2 — Get real market quote
    # ---------------------------------------------------------

    quote = kite.quote(
        [
            f"NFO:{TRADING_SYMBOL}",
            "NSE:NIFTY 50",
        ]
    )

    print("\nREAL ZERODHA QUOTE: RECEIVED")

    # ---------------------------------------------------------
    # STEP 3 — V12.1 Zerodha adapter
    # ---------------------------------------------------------

    adapted = adapt_zerodha_option_quote(
        quote_response=quote,
        trading_symbol=TRADING_SYMBOL,
        instrument_token=INSTRUMENT_TOKEN,
        underlying=UNDERLYING,
    )

    print("\nV12.1 ADAPTER:")
    print(adapted)

    assert adapted["Trading Symbol"] == TRADING_SYMBOL
    assert adapted["Instrument Token"] == INSTRUMENT_TOKEN

    # ---------------------------------------------------------
    # STEP 4 — V12.1 real-market observer
    # ---------------------------------------------------------

    observed = observe_option_market(
        adapted
    )

    print("\nV12.1 OBSERVER:")
    print(observed)

    assert observed["Status"] == "READY"
    assert observed["Data Status"] == "VALID"

    # ---------------------------------------------------------
    # STEP 5 — V12.1 observation record
    # ---------------------------------------------------------

    record = create_option_observation_record(
        observed
    )

    print("\nV12.1 OBSERVATION RECORD:")
    print(record)

    assert record["Status"] == "RECORDED"
    assert record["Data Status"] == "VALID"

    # ---------------------------------------------------------
    # STEP 6 — Create genuine V11 paper position
    # ---------------------------------------------------------

    paper_trade = open_paper_trade(
        trade_id="V12-3-REAL-MARKET-E2E",
        symbol=TRADING_SYMBOL,
        instrument_type="OPTION",
        entry_price=1600.00,
        quantity=65,
        stop_loss=1550.00,
        target=1700.00,
        underlying=UNDERLYING,
        strike=25000,
        option_type="PE",
    )

    print("\nV11 PAPER POSITION:")
    print(paper_trade)

    assert paper_trade["Status"] == "OPEN"
    assert paper_trade["Entry Price"] == 1600.00
    assert paper_trade["Original Quantity"] == 65

    # ---------------------------------------------------------
    # STEP 7 — V12.2 real market → V11 paper bridge
    # ---------------------------------------------------------

    bridged = bridge_real_market_to_paper(
        observation_record=record,
        paper_trade=paper_trade,
    )

    print("\nV12.2 BRIDGE:")
    print(bridged)

    assert bridged["Status"] == "BRIDGED"
    assert bridged["Market Data Status"] == "VALID"

    updated_paper_trade = bridged["Paper Trade"]

    assert (
        updated_paper_trade["Entry Price"]
        == 1600.00
    )

    assert (
        updated_paper_trade["Original Quantity"]
        == 65
    )

    # ---------------------------------------------------------
    # STEP 8 — V12.3 → V10 monitor
    # ---------------------------------------------------------

    monitor_result = monitor_real_market_paper_position(
        observation_record=record,
        paper_trade=updated_paper_trade,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
        holding_minutes=5,
        max_holding_minutes=60,
    )

    print("\nV12.3 → V10 MONITOR:")
    print(monitor_result)

    assert monitor_result["Status"] == "MONITORED"
    assert (
        monitor_result["Market Data Status"]
        == "VALID"
    )

    v10_result = monitor_result["V10 Result"]

    assert isinstance(v10_result, dict)

    print("\nV10 DECISION:")
    print(
        v10_result.get(
            "Decision",
            "Decision field not returned",
        )
    )

    print("\nV10 EXIT REQUIRED:")
    print(
        v10_result.get(
            "Exit Required",
            "Exit field not returned",
        )
    )

    print("\n" + "=" * 65)
    print("V12.3 REAL MARKET → V10 END-TO-END: PASS")
    print("=" * 65)

    print(
        "\nSAFETY CONFIRMATION:"
        "\n- Real market data: YES"
        "\n- V11 paper position: YES"
        "\n- V10 monitor: YES"
        "\n- Paper exit executed: NO"
        "\n- Live order placed: NO"
        "\n- main.py modified: NO"
    )


if __name__ == "__main__":
    main()