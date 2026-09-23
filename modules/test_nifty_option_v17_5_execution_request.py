"""
JKJ AI Trader
V17.5 Stage 3 — Execution Request Validation Test

NO ORDER PLACEMENT.
"""

from modules.nifty_option_v17_5_execution_request import (
    validate_execution_request,
)


def main():

    print("=" * 60)
    print("JKJ V17.5 STAGE 3")
    print("EXECUTION REQUEST VALIDATION")
    print("=" * 60)

    contract_validation = {
        "Status": "CONTRACT_VALIDATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Instrument Token": 14588162,
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Lot Size": 65,
    }

    execution_eligibility = {
        "Status": "EXECUTION_ELIGIBLE",
        "Trading Symbol": "NIFTY2692223300CE",
        "Instrument Token": 14588162,
        "Lot Size": 65,
        "Current Quantity": 130,
        "Requested Exit Quantity": 65,
        "Remaining Quantity": 65,
    }

    # ---------------------------------------------------------
    # TEST 1 — Valid SELL / MARKET / NRML
    # ---------------------------------------------------------

    result = validate_execution_request(
        contract_validation,
        execution_eligibility,
        order_type="MARKET",
        product="NRML",
    )

    print("\nTEST 1 — VALID MARKET SELL / NRML")
    print("--------------------------------")

    print("Status:", result["Status"])
    print("Trading Symbol:", result.get("Trading Symbol"))
    print("Order Type:", result.get("Order Type"))
    print("Product:", result.get("Product"))
    print("Requested Exit Quantity:",
          result.get("Requested Exit Quantity"))
    print("Remaining Quantity:",
          result.get("Remaining Quantity"))
    print("Order Placement Permitted:",
          result["Order Placement Permitted"])

    assert result["Status"] == "EXECUTION_READY"
    assert result["Order Placement Permitted"] is False

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2 — Valid LIMIT / NRML
    # ---------------------------------------------------------

    result = validate_execution_request(
        contract_validation,
        execution_eligibility,
        order_type="LIMIT",
        product="NRML",
    )

    print("\nTEST 2 — VALID LIMIT SELL / NRML")
    print("--------------------------------")

    print("Status:", result["Status"])

    assert result["Status"] == "EXECUTION_READY"

    print("PASS")


    # ---------------------------------------------------------
    # TEST 3 — Invalid product
    # ---------------------------------------------------------

    result = validate_execution_request(
        contract_validation,
        execution_eligibility,
        order_type="MARKET",
        product="INVALID",
    )

    print("\nTEST 3 — INVALID PRODUCT")
    print("------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 4 — Invalid order type
    # ---------------------------------------------------------

    result = validate_execution_request(
        contract_validation,
        execution_eligibility,
        order_type="SL-M",
        product="NRML",
    )

    print("\nTEST 4 — INVALID ORDER TYPE")
    print("---------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 5 — Previous contract validation failed
    # ---------------------------------------------------------

    failed_contract = {
        "Status": "CONTRACT_BLOCKED",
    }

    result = validate_execution_request(
        failed_contract,
        execution_eligibility,
        order_type="MARKET",
        product="NRML",
    )

    print("\nTEST 5 — CONTRACT VALIDATION FAILED")
    print("-----------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6 — Invalid quantity eligibility
    # ---------------------------------------------------------

    invalid_eligibility = {
        "Status": "EXECUTION_BLOCKED",
        "Current Quantity": 65,
        "Requested Exit Quantity": 22,
        "Remaining Quantity": 43,
    }

    result = validate_execution_request(
        contract_validation,
        invalid_eligibility,
        order_type="MARKET",
        product="NRML",
    )

    print("\nTEST 6 — QUANTITY VALIDATION FAILED")
    print("----------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "EXECUTION_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.5 STAGE 3 EXECUTION REQUEST TEST: PASS")
    print("SAFETY GATES VERIFIED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()