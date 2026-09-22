"""
JKJ AI Trader
V17.5 Stage 2 — Zerodha Contract Validation Unit Test

Controlled validation only.
NO ZERODHA SESSION.
NO LIVE ORDER.
"""

from modules.nifty_option_v17_5_zerodha_contract_validation import (
    validate_zerodha_contract,
)


def main():

    print("=" * 60)
    print("JKJ V17.5 STAGE 2")
    print("ZERODHA CONTRACT VALIDATION UNIT TEST")
    print("=" * 60)

    contract = {
        "tradingsymbol": "NIFTY2692223300CE",
        "instrument_token": 14588162,
        "expiry": "2026-09-22",
        "strike": 23300.0,
        "instrument_type": "CE",
        "lot_size": 65,
    }

    instruments = [contract.copy()]

    # ---------------------------------------------------------
    # TEST 1 — Exact contract match
    # ---------------------------------------------------------

    result = validate_zerodha_contract(
        instruments,
        contract,
    )

    print("\nTEST 1 — EXACT CONTRACT MATCH")
    print("-----------------------------")
    print("Status:", result["Status"])

    assert result["Status"] == "CONTRACT_VALIDATED"
    assert result["Trading Symbol"] == "NIFTY2692223300CE"
    assert result["Instrument Token"] == 14588162
    assert result["Strike"] == 23300.0
    assert result["Option Type"] == "CE"
    assert result["Lot Size"] == 65
    assert result["Contract Identity Valid"] is True
    assert result["Order Placement Permitted"] is False

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2 — Wrong instrument token
    # ---------------------------------------------------------

    wrong_token = contract.copy()
    wrong_token["instrument_token"] = 99999999

    result = validate_zerodha_contract(
        instruments,
        wrong_token,
    )

    print("\nTEST 2 — WRONG INSTRUMENT TOKEN")
    print("-------------------------------")
    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CONTRACT_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 3 — Wrong strike
    # ---------------------------------------------------------

    wrong_strike = contract.copy()
    wrong_strike["strike"] = 23400.0

    result = validate_zerodha_contract(
        instruments,
        wrong_strike,
    )

    print("\nTEST 3 — WRONG STRIKE")
    print("---------------------")
    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CONTRACT_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 4 — Wrong lot size
    # ---------------------------------------------------------

    wrong_lot = contract.copy()
    wrong_lot["lot_size"] = 75

    result = validate_zerodha_contract(
        instruments,
        wrong_lot,
    )

    print("\nTEST 4 — WRONG LOT SIZE")
    print("-----------------------")
    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CONTRACT_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 5 — Contract not found
    # ---------------------------------------------------------

    missing_contract = contract.copy()
    missing_contract["tradingsymbol"] = "NIFTY2692223400CE"

    result = validate_zerodha_contract(
        instruments,
        missing_contract,
    )

    print("\nTEST 5 — CONTRACT NOT FOUND")
    print("---------------------------")
    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CONTRACT_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6 — Duplicate contract match
    # ---------------------------------------------------------

    duplicate_instruments = [
        contract.copy(),
        contract.copy(),
    ]

    result = validate_zerodha_contract(
        duplicate_instruments,
        contract,
    )

    print("\nTEST 6 — DUPLICATE CONTRACT")
    print("---------------------------")
    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CONTRACT_BLOCKED"
    assert result["Order Placement Permitted"] is False

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.5 STAGE 2 UNIT TEST: PASS")
    print("EXACT CONTRACT ALLOWED")
    print("INVALID CONTRACTS BLOCKED")
    print("NO ZERODHA SESSION REQUIRED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()
