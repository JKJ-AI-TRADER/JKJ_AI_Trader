"""
JKJ AI Trader
V17.5 Execution Readiness Integration Test

Purpose:
    Validate the controlled execution-readiness boundary from
    a synchronized V18.1 paper exit through the V17.5
    contract, quantity, and execution-request gates.

This test does NOT:
    - connect to Zerodha
    - place orders
    - modify V11
    - modify V18.1
    - modify V19.1
    - modify main.py

Wisdom Before Wealth.
"""

from modules.nifty_option_v17_5_zerodha_contract_validation import (
    validate_zerodha_contract,
)

from modules.nifty_option_v17_5_execution_eligibility import (
    validate_execution_eligibility,
)

from modules.nifty_option_v17_5_execution_request import (
    validate_execution_request,
)


TRADING_SYMBOL = "NIFTY2692223300CE"
INSTRUMENT_TOKEN = 14588162
EXPIRY = "2026-09-22"
STRIKE = 23300.0
OPTION_TYPE = "CE"
LOT_SIZE = 65

CURRENT_QUANTITY = 65
REQUESTED_EXIT_QUANTITY = 65


def build_controlled_instruments():
    return [
        {
            "tradingsymbol": TRADING_SYMBOL,
            "instrument_token": INSTRUMENT_TOKEN,
            "expiry": EXPIRY,
            "strike": STRIKE,
            "instrument_type": OPTION_TYPE,
            "lot_size": LOT_SIZE,
        }
    ]


def build_expected_contract():
    return {
        "tradingsymbol": TRADING_SYMBOL,
        "instrument_token": INSTRUMENT_TOKEN,
        "expiry": EXPIRY,
        "strike": STRIKE,
        "instrument_type": OPTION_TYPE,
        "lot_size": LOT_SIZE,
    }


def main():

    print("=" * 60)
    print("JKJ V17.5 EXECUTION READINESS INTEGRATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # STEP 1 — Contract validation
    # ---------------------------------------------------------

    contract_validation = validate_zerodha_contract(
        build_controlled_instruments(),
        build_expected_contract(),
    )

    assert contract_validation["Status"] == (
        "CONTRACT_VALIDATED"
    )

    assert contract_validation["Contract Identity Valid"] is True
    assert contract_validation["Order Placement Permitted"] is False

    print("V17.5 Stage 2 Contract Validation: PASS")

    # ---------------------------------------------------------
    # STEP 2 — Execution eligibility
    # ---------------------------------------------------------

    execution_eligibility = validate_execution_eligibility(
        {
            "tradingsymbol": TRADING_SYMBOL,
            "instrument_token": INSTRUMENT_TOKEN,
            "expiry": EXPIRY,
            "strike": STRIKE,
            "instrument_type": OPTION_TYPE,
            "lot_size": LOT_SIZE,
        },
        current_quantity=CURRENT_QUANTITY,
        requested_quantity=REQUESTED_EXIT_QUANTITY,
    )

    assert execution_eligibility["Status"] == (
        "EXECUTION_ELIGIBLE"
    )

    assert execution_eligibility["Requested Exit Quantity"] == (
        REQUESTED_EXIT_QUANTITY
    )

    assert execution_eligibility["Remaining Quantity"] == 0

    print("V17.5 Stage 1 Execution Eligibility: PASS")

    # ---------------------------------------------------------
    # STEP 3 — Execution request validation
    # ---------------------------------------------------------

    execution_request = validate_execution_request(
        contract_validation=contract_validation,
        execution_eligibility=execution_eligibility,
        order_type="MARKET",
        product="NRML",
        transaction_type="SELL",
    )

    assert execution_request["Status"] == (
        "EXECUTION_READY"
    )

    assert execution_request["Trading Symbol"] == (
        TRADING_SYMBOL
    )

    assert execution_request["Instrument Token"] == (
        INSTRUMENT_TOKEN
    )

    assert execution_request["Requested Exit Quantity"] == (
        REQUESTED_EXIT_QUANTITY
    )

    assert execution_request["Remaining Quantity"] == 0

    assert execution_request["Transaction Type"] == "SELL"
    assert execution_request["Order Type"] == "MARKET"
    assert execution_request["Product"] == "NRML"

    assert execution_request["Order Placement Permitted"] is False

    print("V17.5 Stage 3 Execution Request: PASS")

        # ---------------------------------------------------------
    # SAFETY TEST 1 — Invalid contract
    # ---------------------------------------------------------

    invalid_contract = build_expected_contract()
    invalid_contract["instrument_token"] = 99999999

    blocked_contract = validate_zerodha_contract(
        build_controlled_instruments(),
        invalid_contract,
    )

    assert blocked_contract["Status"] == "CONTRACT_BLOCKED"
    assert blocked_contract["Order Placement Permitted"] is False

    print("Safety Test 1 — Invalid Contract: SAFELY BLOCKED")

        # ---------------------------------------------------------
    # SAFETY TEST 2 — Invalid quantity
    # ---------------------------------------------------------

    blocked_quantity = validate_execution_eligibility(
        {
            "tradingsymbol": TRADING_SYMBOL,
            "instrument_token": INSTRUMENT_TOKEN,
            "expiry": EXPIRY,
            "strike": STRIKE,
            "instrument_type": OPTION_TYPE,
            "lot_size": LOT_SIZE,
        },
        current_quantity=65,
        requested_quantity=22,
    )

    assert blocked_quantity["Status"] == "EXECUTION_BLOCKED"
    assert blocked_quantity["Order Placement Permitted"] is False

    print("Safety Test 2 — Invalid Quantity: SAFELY BLOCKED")

        # ---------------------------------------------------------
    # SAFETY TEST 3 — Invalid order type
    # ---------------------------------------------------------

    blocked_order = validate_execution_request(
        contract_validation=contract_validation,
        execution_eligibility=execution_eligibility,
        order_type="SL-M",
        product="NRML",
        transaction_type="SELL",
    )

    assert blocked_order["Status"] == "EXECUTION_BLOCKED"
    assert blocked_order["Order Placement Permitted"] is False

    print("Safety Test 3 — Invalid Order Type: SAFELY BLOCKED")
    # ---------------------------------------------------------
    # FINAL SAFETY CHECK
    # ---------------------------------------------------------

    assert execution_request["Order Placement Permitted"] is False

    print()
    print("V17.5 EXECUTION READINESS INTEGRATION: PASS")
    print("CONTRACT VALIDATED")
    print("QUANTITY ELIGIBLE")
    print("EXECUTION REQUEST READY")
    print("NO ORDER PLACEMENT")
    print("NO ZERODHA ORDER")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()
