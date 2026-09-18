"""
JKJ AI Trader
V17.6.2 — Candidate Affordability Test

NO LIVE ORDER.
"""

from modules.nifty_option_v17_6_candidate_affordability import (
    evaluate_candidate_affordability,
)


def main():

    print("=" * 60)
    print("JKJ V17.6.2")
    print("CANDIDATE AFFORDABILITY ENGINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1
    # ₹25,000 available
    # ₹300 option price
    # Lot size 65
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=300,
        lot_size=65,
        available_capital=25000,
    )

    print("\nTEST 1 — ₹25,000 / ₹300 OPTION / LOT 65")
    print("-----------------------------------------")

    print("Status:", result["Status"])
    print("Affordable Lots:",
          result["Affordable Lots"])
    print("Maximum Affordable Quantity:",
          result["Maximum Affordable Quantity"])
    print("Estimated Capital Required:",
          result["Estimated Capital Required"])
    print("Unused Candidate Capital:",
          result["Unused Candidate Capital"])

    assert result["Status"] == "CANDIDATE_AFFORDABLE"
    assert result["Affordable Lots"] == 1
    assert result["Maximum Affordable Quantity"] == 65
    assert result["Estimated Capital Required"] == 19500

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2
    # ₹25,000 available
    # ₹100 option price
    # Lot size 65
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=100,
        lot_size=65,
        available_capital=25000,
    )

    print("\nTEST 2 — ₹25,000 / ₹100 OPTION / LOT 65")
    print("----------------------------------------")

    print("Status:", result["Status"])
    print("Affordable Lots:",
          result["Affordable Lots"])
    print("Maximum Affordable Quantity:",
          result["Maximum Affordable Quantity"])
    print("Estimated Capital Required:",
          result["Estimated Capital Required"])

    assert result["Status"] == "CANDIDATE_AFFORDABLE"
    assert result["Affordable Lots"] == 3
    assert result["Maximum Affordable Quantity"] == 195
    assert result["Estimated Capital Required"] == 19500

    print("PASS")


    # ---------------------------------------------------------
    # TEST 3
    # Candidate-specific allocation limit
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=300,
        lot_size=65,
        available_capital=25000,
        max_candidate_allocation=20000,
    )

    print("\nTEST 3 — ₹20,000 MAX CANDIDATE ALLOCATION")
    print("----------------------------------------")

    print("Status:", result["Status"])
    print("Candidate Budget:",
          result["Candidate Budget"])
    print("Affordable Lots:",
          result["Affordable Lots"])
    print("Maximum Affordable Quantity:",
          result["Maximum Affordable Quantity"])

    assert result["Status"] == "CANDIDATE_AFFORDABLE"
    assert result["Candidate Budget"] == 20000
    assert result["Affordable Lots"] == 1
    assert result["Maximum Affordable Quantity"] == 65
    assert result["Estimated Capital Required"] == 19500

    print("PASS")


    # ---------------------------------------------------------
    # TEST 4
    # Insufficient capital for one lot
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=500,
        lot_size=65,
        available_capital=25000,
    )

    print("\nTEST 4 — INSUFFICIENT CAPITAL")
    print("-----------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CANDIDATE_NOT_AFFORDABLE"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 5
    # Zero capital
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=100,
        lot_size=65,
        available_capital=0,
    )

    print("\nTEST 5 — ZERO CAPITAL")
    print("---------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CANDIDATE_NOT_AFFORDABLE"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6
    # Invalid lot size
    # ---------------------------------------------------------

    result = evaluate_candidate_affordability(
        entry_price=100,
        lot_size=0,
        available_capital=25000,
    )

    print("\nTEST 6 — INVALID LOT SIZE")
    print("-------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CANDIDATE_NOT_AFFORDABLE"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.6.2 CANDIDATE AFFORDABILITY TEST: PASS")
    print("AFFORDABLE QUANTITY CALCULATED")
    print("CAPITAL LIMITS RESPECTED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()