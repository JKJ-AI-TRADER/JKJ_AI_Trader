"""
JKJ AI Trader
V17.6.1 — Capital Availability & Reserve Test

NO LIVE ORDER.
"""

from modules.nifty_option_v17_6_capital_engine import (
    evaluate_available_capital,
)


def main():

    print("=" * 60)
    print("JKJ V17.6.1")
    print("CAPITAL AVAILABILITY & RESERVE ENGINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1 — ₹30,000 available, ₹5,000 reserve
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=30000,
        reserve_amount=5000,
    )

    print("\nTEST 1 — ₹30,000 FUNDS / ₹5,000 RESERVE")
    print("----------------------------------------")

    print("Status:", result["Status"])
    print("Available Funds:",
          result["Available Funds"])
    print("JKJ Reserve:",
          result["JKJ Reserve"])
    print("Usable Trading Capital:",
          result["Usable Trading Capital"])

    assert result["Status"] == "CAPITAL_AVAILABLE"
    assert result["Usable Trading Capital"] == 25000
    assert result["Capital Reserve Protected"] is True

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2 — Reserve equals available funds
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=30000,
        reserve_amount=30000,
    )

    print("\nTEST 2 — FULL CAPITAL RESERVED")
    print("-------------------------------")

    print("Status:", result["Status"])
    print("Usable Trading Capital:",
          result["Usable Trading Capital"])

    assert result["Status"] == "CAPITAL_AVAILABLE"
    assert result["Usable Trading Capital"] == 0

    print("PASS — NO CAPITAL AVAILABLE")


    # ---------------------------------------------------------
    # TEST 3 — Reserve exceeds available funds
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=30000,
        reserve_amount=35000,
    )

    print("\nTEST 3 — RESERVE EXCEEDS FUNDS")
    print("------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])
    print("Usable Trading Capital:",
          result["Usable Trading Capital"])

    assert result["Status"] == "CAPITAL_BLOCKED"
    assert result["Usable Trading Capital"] == 0

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 4 — Zero available funds
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=0,
        reserve_amount=0,
    )

    print("\nTEST 4 — ZERO AVAILABLE FUNDS")
    print("-----------------------------")

    print("Status:", result["Status"])
    print("Usable Trading Capital:",
          result["Usable Trading Capital"])

    assert result["Status"] == "CAPITAL_AVAILABLE"
    assert result["Usable Trading Capital"] == 0

    print("PASS — NO CAPITAL AVAILABLE")


    # ---------------------------------------------------------
    # TEST 5 — Negative funds
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=-1000,
        reserve_amount=0,
    )

    print("\nTEST 5 — NEGATIVE FUNDS")
    print("-----------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CAPITAL_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6 — Negative reserve
    # ---------------------------------------------------------

    result = evaluate_available_capital(
        available_funds=30000,
        reserve_amount=-5000,
    )

    print("\nTEST 6 — NEGATIVE RESERVE")
    print("-------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CAPITAL_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.6.1 CAPITAL ENGINE TEST: PASS")
    print("CAPITAL RESERVE PROTECTED")
    print("USABLE CAPITAL CALCULATED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()