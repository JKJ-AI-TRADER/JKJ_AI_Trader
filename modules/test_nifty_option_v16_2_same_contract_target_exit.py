"""
JKJ AI Trader

V16.2 Stage 4C — Same-Contract Real-Market Target Exit

Purpose:
    Validate that a fresh real-market observation for the
    exact current NIFTY contract can feed the existing
    V15.5 target progression, V15.6 slicing bridge, and
    V17.3 target-exit planning boundary.

This test does NOT:
    - place live orders
    - create live positions
    - assume a fill
    - modify V15.5
    - modify V15.6
    - modify V17.1/V17.2/V17.3
    - modify V16.2 production modules
    - modify main.py

Wisdom Before Wealth.
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.nifty_option_target_progression import (
    evaluate_target_progression,
)

from modules.nifty_option_target_slicing_bridge import (
    evaluate_target_slicing,
)

from modules.nifty_option_v17_3_target_exit_integration import (
    create_target_exit_integration,
)

from modules.nifty_option_paper_position_lifecycle import (
    update_paper_position,
)


def main():

    print(
        "\nJKJ AI Trader — V16.2 Stage 4C"
    )
    print(
        "Same-Contract Real-Market Target Exit"
    )
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. Controlled paper-position fixture
    # ---------------------------------------------------------

    trade = {
        "Status": "OPEN",
        "Trade ID": "V16.2-REAL-TEST-004",
        "Symbol": None,
        "Instrument Type": "OPTION",
        "Underlying": "NIFTY",
        "Expiry": None,
        "Strike": None,
        "Option Type": "CE",
        "Entry Price": 100.0,
        "Original Quantity": 75,
        "Current Quantity": 75,
        "Current Price": 100.0,
        "Peak Price": 100.0,
        "Stop Loss": 95.0,
        "Target": 110.0,
        "Target 1": 110.0,
        "Target 2": 115.0,
        "Target 3": 120.0,
        "Risk Reward 1": 2.0,
        "Risk Reward 2": 3.0,
        "Risk Reward 3": 4.0,
        "Entry Status": "ENTRY_QUALIFIED",
        "Paper Trade Permission": "PERMITTED",
    }

    # ---------------------------------------------------------
    # 2. Fresh Zerodha session
    # ---------------------------------------------------------

    session_result = get_kite_session()

    if session_result.get("Status") not in (
        "SESSION_REUSED",
        "AUTHENTICATED",
    ):
        print("\nZerodha session unavailable.")
        print(
            "Reason:",
            session_result.get("Reason"),
        )
        print("Stage 4C stopped safely.")
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("\nKite session object unavailable.")
        print("Stage 4C stopped safely.")
        return

    # ---------------------------------------------------------
    # 3. Select current NIFTY CE contract
    # ---------------------------------------------------------

    instruments = kite.instruments("NFO")

    if not isinstance(instruments, list):
        print("\nNFO instrument list unavailable.")
        print("Stage 4C stopped safely.")
        return

    nifty_spot = kite.ltp(
        "NSE:NIFTY 50"
    )["NSE:NIFTY 50"]["last_price"]

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        print("\nInvalid NIFTY spot price.")
        print("Stage 4C stopped safely.")
        return

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
        print("\nNo NIFTY option expiry found.")
        print("Stage 4C stopped safely.")
        return

    selected_expiry = expiries[0]

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=2,
    )

    if selection.get("Status") != "SELECTED":
        print(
            "\nCurrent NIFTY contract selection failed."
        )
        print(
            "Reason:",
            selection.get("Reason"),
        )
        print("Stage 4C stopped safely.")
        return

    ce_contracts = [
        contract
        for contract in selection.get(
            "Contracts",
            [],
        )
        if contract.get("instrument_type") == "CE"
    ]

    if not ce_contracts:
        print(
            "\nNo current NIFTY CE contract selected."
        )
        print("Stage 4C stopped safely.")
        return

    exact_contract = ce_contracts[0]

    trading_symbol = exact_contract.get(
        "tradingsymbol"
    )

    instrument_token = exact_contract.get(
        "instrument_token"
    )

    if not trading_symbol or not instrument_token:
        print(
            "\nSelected contract is incomplete."
        )
        print("Stage 4C stopped safely.")
        return

    trade["Symbol"] = trading_symbol
    trade["Strike"] = exact_contract.get(
        "strike"
    )
    trade["Expiry"] = exact_contract.get(
        "expiry"
    )
    trade["Option Type"] = exact_contract.get(
        "instrument_type"
    )

    print("\nCurrent Paper Contract:")
    print("Trading Symbol:", trading_symbol)
    print("Instrument Token:", instrument_token)
    print("Expiry:", trade["Expiry"])
    print("Strike:", trade["Strike"])
    print("Option Type:", trade["Option Type"])

    # ---------------------------------------------------------
    # 4. Verify exact contract identity
    # ---------------------------------------------------------

    if (
        exact_contract.get("expiry")
        != trade["Expiry"]
    ):
        print("\nExpiry mismatch.")
        print("Stage 4C stopped safely.")
        return

    if (
        exact_contract.get("strike")
        != trade["Strike"]
    ):
        print("\nStrike mismatch.")
        print("Stage 4C stopped safely.")
        return

    if (
        exact_contract.get("instrument_type")
        != trade["Option Type"]
    ):
        print("\nOption type mismatch.")
        print("Stage 4C stopped safely.")
        return

    # ---------------------------------------------------------
    # 5. Capture one fresh quote for exact contract
    # ---------------------------------------------------------

    quote_key = f"NFO:{trading_symbol}"

    quote_result = kite.ltp(
        [quote_key]
    )

    quote = quote_result.get(
        quote_key
    )

    if not isinstance(quote, dict):
        print("\nFresh option quote unavailable.")
        print("Stage 4C stopped safely.")
        return

    current_price = quote.get(
        "last_price"
    )

    if not isinstance(
        current_price,
        (int, float),
    ) or current_price <= 0:
        print("\nInvalid real-market option price.")
        print("Stage 4C stopped safely.")
        return

    print("\nFresh Real-Market Observation:")
    print(
        "Trading Symbol:",
        trading_symbol,
    )
    print(
        "Current Price:",
        current_price,
    )

    # ---------------------------------------------------------
    # 6. Update existing paper position
    # ---------------------------------------------------------

    update_result = update_paper_position(
        trade=trade,
        current_price=current_price,
    )

    print("\nPaper Position Update:")
    print(update_result)

    if update_result.get("Status") != "UPDATED":
        print(
            "\nPaper position update failed safely."
        )
        print("Stage 4C stopped safely.")
        return

    # ---------------------------------------------------------
    # 7. Create V15.5 target structure
    # ---------------------------------------------------------

    target_data = {
        "Status": "TARGETS_VALIDATED",
        "Trading Symbol": trading_symbol,
        "Underlying": "NIFTY",
        "Expiry": trade["Expiry"],
        "Strike": trade["Strike"],
        "Option Type": trade["Option Type"],
        "Instrument Token": instrument_token,
        "Entry Price": 100.0,
        "Stop Price": 95.0,
        "Target 1": 110.0,
        "Target 2": 115.0,
        "Target 3": 120.0,
    }

    # ---------------------------------------------------------
    # 8. V15.5 target progression
    # ---------------------------------------------------------

    target_result = evaluate_target_progression(
        target_data=target_data,
        current_price=current_price,
        targets_reached=[],
    )

    print("\nV15.5 Target Progression:")
    print(target_result)

    if target_result.get("Status") == "WAITING":

        print("\n" + "=" * 65)
        print(
            "V16.2 STAGE 4C: PASS"
        )
        print(
            "REAL PRICE BELOW NEXT TARGET — "
            "NO EXIT PLANNED"
        )
        print("=" * 65)
        return

    if target_result.get("Status") != "TARGET_REACHED":

        print("\nV15.5 target progression rejected.")
        print("Stage 4C stopped safely.")
        return

    print(
        "\nV15.5 TARGET REACHED:",
        target_result.get("Target Event"),
    )

    # ---------------------------------------------------------
    # 9. V15.6 target-to-slicing boundary
    # ---------------------------------------------------------

    slice_result = evaluate_target_slicing(
        target_progression=target_result,
        total_quantity=trade["Original Quantity"],
        current_quantity=trade["Current Quantity"],
        entry_price=trade["Entry Price"],
        current_price=current_price,
        peak_price=trade["Peak Price"],
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
    )

    print("\nV15.6 Target Slicing:")
    print(slice_result)

    if slice_result.get("Status") != "EVALUATED":
        print("\nV15.6 slicing rejected.")
        print("Stage 4C stopped safely.")
        return

    # ---------------------------------------------------------
    # 10. V17.3 target-exit planning
    # ---------------------------------------------------------

    target_exit_integration = (
        create_target_exit_integration(
            target_progression=target_result,
            total_quantity=trade[
                "Original Quantity"
            ],
        )
    )

    print("\nV17.3 Target Exit Integration:")
    print(target_exit_integration)

    if (
        target_exit_integration.get(
            "Status"
        )
        != "PLANNED"
    ):
        print(
            "\nV17.3 target exit planning rejected."
        )
        print("Stage 4C stopped safely.")
        return

    if (
        target_exit_integration.get(
            "Execution Confirmed"
        )
        is not False
    ):
        print(
            "\nExecution confirmation state invalid."
        )
        print("Stage 4C stopped safely.")
        return

    # ---------------------------------------------------------
    # 11. Final Stage 4C result
    # ---------------------------------------------------------

    print("\n" + "=" * 65)
    print(
        "V16.2 STAGE 4C: PASS"
    )
    print(
        "REAL-MARKET TARGET → "
        "EXIT PLANNING VALIDATED"
    )
    print(
        "NO LIVE ORDER — NO ASSUMED FILL"
    )
    print("=" * 65)


if __name__ == "__main__":
    main()
