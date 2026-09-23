"""
JKJ AI Trader
V17.5 Stage 2 — Zerodha Contract Validation Test

NO ORDER PLACEMENT.
"""

from modules.intraday_zerodha_session_manager import get_kite_session
from modules.nifty_option_v17_5_zerodha_contract_validation import (
    validate_zerodha_contract,
)


def main():

    print("=" * 60)
    print("JKJ V17.5 STAGE 2")
    print("ZERODHA CONTRACT VALIDATION")
    print("=" * 60)

    session = get_kite_session()

    if session.get("Status") != "SESSION_REUSED":
        print("SESSION STATUS:", session.get("Status"))
        print("SAFE STOP — Zerodha session unavailable")
        return

    kite = session["Kite"]

    instruments = kite.instruments("NFO")

    print("NFO INSTRUMENTS:", len(instruments))

    expected_contract = {
        "tradingsymbol": "NIFTY2692223300CE",
        "instrument_token": 14588162,
        "expiry": None,
        "strike": 23300.0,
        "instrument_type": "CE",
        "lot_size": 65,
    }

    # ---------------------------------------------------------
    # First obtain the exact live contract.
    # ---------------------------------------------------------

    matches = [
        instrument
        for instrument in instruments
        if instrument.get("tradingsymbol")
        == expected_contract["tradingsymbol"]
    ]

    if len(matches) != 1:
        print(
            "SAFE STOP — Expected one exact contract, found:",
            len(matches),
        )
        return

    exact_contract = matches[0]

    # Use Zerodha's actual current contract values.
    expected_contract["expiry"] = exact_contract["expiry"]

    print("\nEXPECTED CONTRACT")
    print("-----------------")
    print("Trading Symbol:", expected_contract["tradingsymbol"])
    print("Instrument Token:", expected_contract["instrument_token"])
    print("Expiry:", expected_contract["expiry"])
    print("Strike:", expected_contract["strike"])
    print("Option Type:", expected_contract["instrument_type"])
    print("Lot Size:", expected_contract["lot_size"])

    # ---------------------------------------------------------
    # Validate against complete NFO instrument master.
    # ---------------------------------------------------------

    result = validate_zerodha_contract(
        instruments,
        expected_contract,
    )

    print("\nVALIDATION RESULT")
    print("-----------------")
    print("Status:", result["Status"])

    if result["Status"] == "CONTRACT_VALIDATED":

        print("Trading Symbol:", result["Trading Symbol"])
        print("Instrument Token:", result["Instrument Token"])
        print("Expiry:", result["Expiry"])
        print("Strike:", result["Strike"])
        print("Option Type:", result["Option Type"])
        print("Lot Size:", result["Lot Size"])
        print("Contract Identity Valid:",
              result["Contract Identity Valid"])
        print("Order Placement Permitted:",
              result["Order Placement Permitted"])

        print("\nV17.5 STAGE 2: PASS")
        print("EXACT ZERODHA CONTRACT VALIDATED")
        print("NO ORDER PLACED")

    else:

        print("Reason:", result["Reason"])
        print("Order Placement Permitted:",
              result["Order Placement Permitted"])

        print("\nV17.5 STAGE 2: SAFE BLOCK")
        print("NO ORDER PLACED")


if __name__ == "__main__":
    main()