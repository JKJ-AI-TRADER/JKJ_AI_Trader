"""
JKJ AI Trader
V17.5 Stage 2 — Zerodha Contract Validation

Purpose:
    Validate an exact NIFTY option contract against the
    current Zerodha NFO instrument master.

Important:
    This module:
    - reads Zerodha instrument data
    - validates contract identity
    - validates lot size
    - does NOT place orders
    - does NOT create positions
    - does NOT modify V11/V14/V15/V17 modules
    - does NOT modify main.py

Wisdom Before Wealth.
"""


def validate_zerodha_contract(instruments, expected_contract):
    """
    Validate an exact option contract against Zerodha NFO instruments.

    Returns:
        Status = CONTRACT_VALIDATED
        or
        Status = CONTRACT_BLOCKED
    """

    if not isinstance(instruments, list):
        return _blocked("Invalid instruments data")

    if not isinstance(expected_contract, dict):
        return _blocked("Invalid expected contract")

    required_fields = [
        "tradingsymbol",
        "instrument_token",
        "expiry",
        "strike",
        "instrument_type",
        "lot_size",
    ]

    missing = [
        field
        for field in required_fields
        if expected_contract.get(field) is None
    ]

    if missing:
        return _blocked(
            "Missing expected contract fields: "
            + ", ".join(missing)
        )

    symbol = expected_contract["tradingsymbol"]

    matches = [
        instrument
        for instrument in instruments
        if instrument.get("tradingsymbol") == symbol
    ]

    if not matches:
        return _blocked(
            f"Contract not found in Zerodha NFO instruments: {symbol}"
        )

    if len(matches) != 1:
        return _blocked(
            f"Expected exactly one contract match, found {len(matches)}"
        )

    actual = matches[0]

    checks = {
        "instrument_token": (
            actual.get("instrument_token")
            == expected_contract["instrument_token"]
        ),
        "tradingsymbol": (
            actual.get("tradingsymbol")
            == expected_contract["tradingsymbol"]
        ),
        "expiry": (
            actual.get("expiry")
            == expected_contract["expiry"]
        ),
        "strike": (
            float(actual.get("strike"))
            == float(expected_contract["strike"])
        ),
        "instrument_type": (
            actual.get("instrument_type")
            == expected_contract["instrument_type"]
        ),
        "lot_size": (
            int(actual.get("lot_size"))
            == int(expected_contract["lot_size"])
        ),
    }

    failed_checks = [
        field
        for field, passed in checks.items()
        if not passed
    ]

    if failed_checks:
        return {
            "Status": "CONTRACT_BLOCKED",
            "Trading Symbol": symbol,
            "Reason": (
                "Contract identity mismatch: "
                + ", ".join(failed_checks)
            ),
            "Validation Checks": checks,
            "Order Placement Permitted": False,
        }

    return {
        "Status": "CONTRACT_VALIDATED",

        "Trading Symbol": actual["tradingsymbol"],
        "Instrument Token": actual["instrument_token"],
        "Expiry": actual["expiry"],
        "Strike": actual["strike"],
        "Option Type": actual["instrument_type"],
        "Lot Size": actual["lot_size"],

        "Validation Checks": checks,

        "Contract Identity Valid": True,
        "Order Placement Permitted": False,

        "Wisdom Before Wealth": True,
    }


def _blocked(reason):
    return {
        "Status": "CONTRACT_BLOCKED",
        "Reason": reason,
        "Contract Identity Valid": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }