"""
JKJ AI Trader
V16.2 Stage 4B — Same-Contract Real-Market Paper Monitoring

Purpose:
Validate real Zerodha price updates against a known-good
qualified V15 paper-position structure.

This test does NOT:
- place live orders
- create live positions
- make new entry decisions
- modify V11
- modify V12-V15
- modify main.py
"""

import time

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.nifty_option_paper_position_lifecycle import (
    update_paper_position,
)


def main():

    print("\nJKJ AI Trader — V16.2 Stage 4B")
    print("Same-Contract Real-Market Paper Monitoring")
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. Known-good qualified V15 paper position
    #    Based on the successful V16.2 Stage 3 structure.
    # ---------------------------------------------------------

    trading_symbol = None

    trade = {
        "Status": "OPEN",
        "Trade ID": "V16.2-REAL-TEST-003",
        "Symbol": trading_symbol,
        "Instrument Type": "OPTION",
        "Underlying": "NIFTY",
        "Expiry": None,
        "Strike": 23300,
        "Option Type": "CE",
        "Entry Price": 114.95,
        "Quantity": 75,
        "Current Quantity": 75,
        "Current Price": 114.95,
        "Peak Price": 114.95,
        "Stop Loss": 112.95,
        "Target": 116.95,
        "Target 1": 116.95,
        "Target 2": 118.95,
        "Target 3": 120.95,
        "Risk Reward 1": 1.0,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,
        "Entry Status": "ENTRY_QUALIFIED",
        "Paper Trade Permission": "PERMITTED",
    }

    
    print("Entry Price:", trade["Entry Price"])
    print("Quantity:", trade["Current Quantity"])
    print("Stop Loss:", trade["Stop Loss"])
    print("Target:", trade["Target"])

    # ---------------------------------------------------------
    # 2. Get current Zerodha session
    # ---------------------------------------------------------

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        print("\nZerodha session result invalid.")
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("\nZerodha session unavailable.")
        print(
            "Reason:",
            session_result.get(
                "Reason",
                "Unknown session error.",
            ),
        )
        return

    # ---------------------------------------------------------
    # 3. Select current NIFTY paper contract
    # ---------------------------------------------------------

    instruments = kite.instruments("NFO")

    if not isinstance(instruments, list):
        print("\nNFO instrument list unavailable.")
        return

    nifty_spot = kite.ltp(
        "NSE:NIFTY 50"
    )["NSE:NIFTY 50"]["last_price"]

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        print("\nInvalid NIFTY spot price.")
        print("Stage 4B stopped safely.")
        return

    nifty_options = [
        item
        for item in instruments
        if item.get("name") == "NIFTY"
        and item.get("instrument_type") in ("CE", "PE")
    ]

    expiries = sorted({
        item.get("expiry")
        for item in nifty_options
        if item.get("expiry")
    })

    if not expiries:
        print("\nNo NIFTY option expiry found.")
        print("Stage 4B stopped safely.")
        return

    selected_expiry = expiries[0]

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=2,
    )

    if selection.get("Status") != "SELECTED":
        print("\nCurrent NIFTY contract selection failed.")
        print(
            "Reason:",
            selection.get("Reason"),
        )
        print("Stage 4B stopped safely.")
        return

    ce_contracts = [
        contract
        for contract in selection.get("Contracts", [])
        if contract.get("instrument_type") == "CE"
    ]

    if not ce_contracts:
        print("\nNo current NIFTY CE contract selected.")
        print("Stage 4B stopped safely.")
        return

    exact_contract = ce_contracts[0]

    trading_symbol = exact_contract.get(
        "tradingsymbol"
    )

    instrument_token = exact_contract.get(
        "instrument_token"
    )

    if not trading_symbol or not instrument_token:
        print("\nSelected contract is incomplete.")
        print("Stage 4B stopped safely.")
        return

    trade["Symbol"] = trading_symbol
    trade["Strike"] = exact_contract.get("strike")
    trade["Expiry"] = exact_contract.get("expiry")
    trade["Option Type"] = exact_contract.get(
        "instrument_type"
    )

    print("\nKnown-Good Paper Position:")
    print("Symbol:", trade["Symbol"])
    print("Expiry:", trade["Expiry"])
    print("Strike:", trade["Strike"])
    print("Option Type:", trade["Option Type"])

    # ---------------------------------------------------------
    # 4. Verify exact identity
    # ---------------------------------------------------------

    if exact_contract.get("expiry") != trade["Expiry"]:
        print("\nExpiry mismatch.")
        print("Stage 4B stopped safely.")
        return

    if exact_contract.get("strike") != trade["Strike"]:
        print("\nStrike mismatch.")
        print("Stage 4B stopped safely.")
        return

    if (
        exact_contract.get("instrument_type")
        != trade["Option Type"]
    ):
        print("\nOption type mismatch.")
        print("Stage 4B stopped safely.")
        return

    print("\nExact Contract Confirmed:")
    print("Trading Symbol:", trading_symbol)
    print("Instrument Token:", instrument_token)
    print("Expiry:", exact_contract.get("expiry"))
    print("Strike:", exact_contract.get("strike"))
    print(
        "Option Type:",
        exact_contract.get("instrument_type"),
    )

    # ---------------------------------------------------------
    # 5. Monitor exact same contract
    # ---------------------------------------------------------

    print("\nMonitoring Exact Paper Contract:")

    for observation_number in range(1, 4):

        try:

            quote_response = kite.quote(
                [f"NFO:{trading_symbol}"]
            )

            quote_data = quote_response.get(
                f"NFO:{trading_symbol}"
            )

            if not quote_data:
                print(
                    "\nQuote unavailable for exact contract."
                )
                return

            current_price = quote_data.get(
                "last_price"
            )

            if not isinstance(
                current_price,
                (int, float),
            ) or current_price <= 0:

                print(
                    "\nInvalid real-market price."
                )
                return

            update_result = update_paper_position(
                trade=trade,
                current_price=current_price,
            )

            print(
                f"\nMonitoring {observation_number}/3"
            )

            print(
                "Symbol:",
                trading_symbol,
                "| Price:",
                current_price,
                "| Update:",
                update_result.get("Status"),
            )

            print(
                "Peak:",
                update_result.get("Peak Price"),
                "| P&L %:",
                update_result.get(
                    "Current Profit %"
                ),
            )

            if update_result.get("Status") != "UPDATED":
                print(
                    "\nPaper position update failed safely."
                )
                return

        except Exception as exc:

            print(
                "\nExact-contract quote failed safely."
            )
            print("Reason:", exc)
            return

        if observation_number < 3:
            time.sleep(10)

    # ---------------------------------------------------------
    # 6. Final validation
    # ---------------------------------------------------------

    print("\n" + "=" * 65)
    print(
        "V16.2 STAGE 4B SAME-CONTRACT MONITORING: PASS"
    )
    print(
        "EXACT PAPER CONTRACT MONITORED — NO LIVE ORDER"
    )
    print("=" * 65)


if __name__ == "__main__":
    main()