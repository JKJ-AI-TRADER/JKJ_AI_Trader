"""
JKJ AI Trader
V17.5 Execution Eligibility Test

Validation only.
NO LIVE ORDER.
"""

from modules.nifty_option_v17_5_execution_eligibility import (
    validate_execution_eligibility,
)


def print_result(name, result):
    print(f"\n{name}")
    print("-" * len(name))
    print("Status:", result["Status"])

    if result["Status"] == "EXECUTION_ELIGIBLE":
        print("Trading Symbol:", result["Trading Symbol"])
        print("Instrument Token:", result["Instrument Token"])
        print("Expiry:", result["Expiry"])
        print("Strike:", result["Strike"])
        print("Option Type:", result["Option Type"])
        print("Lot Size:", result["Lot Size"])
        print("Current Quantity:", result["Current Quantity"])
        print("Requested Exit Quantity:", result["Requested Exit Quantity"])
        print("Remaining Quantity:", result["Remaining Quantity"])
        print("Order Placement Permitted:",
              result["Order Placement Permitted"])
    else:
        print("Reason:", result["Reason"])
        print("Order Placement Permitted:",
              result["Order Placement Permitted"])


def main():

    contract = {
        "tradingsymbol": "NIFTY2692223300CE",
        "instrument_token": 14588162,
        "expiry": "2026-09-22",
        "strike": 23300.0,
        "instrument_type": "CE",
        "lot_size": 65,
    }

    # ---------------------------------------------------------
    # TEST 1 — Valid complete exit
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=65,
        requested_quantity=65,
    )

    print_result(
        "TEST 1 — FULL EXIT 65 / 65",
        result,
    )

    assert result["Status"] == "EXECUTION_ELIGIBLE"
    assert result["Remaining Quantity"] == 0

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2 — Valid partial exit of one lot
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=130,
        requested_quantity=65,
    )

    print_result(
        "TEST 2 — ONE LOT EXIT 65 / 130",
        result,
    )

    assert result["Status"] == "EXECUTION_ELIGIBLE"
    assert result["Remaining Quantity"] == 65

    print("PASS")


    # ---------------------------------------------------------
    # TEST 3 — Invalid paper slice 22
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=65,
        requested_quantity=22,
    )

    print_result(
        "TEST 3 — INVALID SLICE 22 / 65",
        result,
    )

    assert result["Status"] == "EXECUTION_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 4 — Invalid quantity 20
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=65,
        requested_quantity=20,
    )

    print_result(
        "TEST 4 — INVALID SLICE 20 / 65",
        result,
    )

    assert result["Status"] == "EXECUTION_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 5 — Requested quantity exceeds position
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=65,
        requested_quantity=130,
    )

    print_result(
        "TEST 5 — EXIT EXCEEDS POSITION",
        result,
    )

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6 — Invalid current position
    # ---------------------------------------------------------

    result = validate_execution_eligibility(
        contract,
        current_quantity=75,
        requested_quantity=65,
    )

    print_result(
        "TEST 6 — INVALID CURRENT POSITION 75",
        result,
    )

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.5 EXECUTION ELIGIBILITY TEST: PASS")
    print("VALID QUANTITIES ALLOWED")
    print("INVALID QUANTITIES BLOCKED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()