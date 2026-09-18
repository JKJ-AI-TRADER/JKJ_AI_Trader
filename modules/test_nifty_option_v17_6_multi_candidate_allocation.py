"""
JKJ AI Trader
V17.6.3 — Multi-Candidate Capital Allocation Test

NO LIVE ORDER.
"""

from modules.nifty_option_v17_6_multi_candidate_allocation import (
    allocate_capital,
)


def main():

    print("=" * 60)
    print("JKJ V17.6.3")
    print("MULTI-CANDIDATE CAPITAL ALLOCATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1
    # ₹30,000 usable
    # Candidate A = ₹20,000
    # Candidate B = ₹10,000
    # ---------------------------------------------------------

    candidates = [
        {
            "Candidate": "NIFTY CE A",
            "Maximum Allocation": 20000,
        },
        {
            "Candidate": "NIFTY PE B",
            "Maximum Allocation": 10000,
        },
    ]

    result = allocate_capital(
        usable_capital=30000,
        candidates=candidates,
    )

    print("\nTEST 1 — ₹20K + ₹10K")
    print("---------------------")

    print("Status:", result["Status"])

    for allocation in result["Allocations"]:
        print(
            allocation["Candidate"],
            "→ ₹",
            allocation["Allocated Capital"],
        )

    print(
        "Total Allocated:",
        result["Total Allocated Capital"],
    )

    print(
        "Remaining Capital:",
        result["Remaining Capital"],
    )

    assert result["Status"] == "CAPITAL_ALLOCATED"
    assert result["Total Allocated Capital"] == 30000
    assert result["Remaining Capital"] == 0

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2
    # More candidates than available capital
    # ---------------------------------------------------------

    candidates = [
        {
            "Candidate": "Candidate A",
            "Maximum Allocation": 20000,
        },
        {
            "Candidate": "Candidate B",
            "Maximum Allocation": 10000,
        },
        {
            "Candidate": "Candidate C",
            "Maximum Allocation": 15000,
        },
    ]

    result = allocate_capital(
        usable_capital=30000,
        candidates=candidates,
    )

    print("\nTEST 2 — THREE CANDIDATES / ₹30K")
    print("--------------------------------")

    for allocation in result["Allocations"]:
        print(
            allocation["Candidate"],
            "→ ₹",
            allocation["Allocated Capital"],
            "(",
            allocation["Allocation Status"],
            ")",
        )

    print(
        "Total Allocated:",
        result["Total Allocated Capital"],
    )

    print(
        "Remaining Capital:",
        result["Remaining Capital"],
    )

    assert result["Total Allocated Capital"] == 30000
    assert result["Remaining Capital"] == 0

    print("PASS")


    # ---------------------------------------------------------
    # TEST 3
    # Capital less than total candidate requirements
    # ---------------------------------------------------------

    candidates = [
        {
            "Candidate": "Candidate A",
            "Maximum Allocation": 12000,
        },
        {
            "Candidate": "Candidate B",
            "Maximum Allocation": 8000,
        },
        {
            "Candidate": "Candidate C",
            "Maximum Allocation": 7000,
        },
    ]

    result = allocate_capital(
        usable_capital=25000,
        candidates=candidates,
    )

    print("\nTEST 3 — ₹25K / REQUIREMENTS ₹27K")
    print("--------------------------------")

    for allocation in result["Allocations"]:
        print(
            allocation["Candidate"],
            "→ ₹",
            allocation["Allocated Capital"],
        )

    print(
        "Total Allocated:",
        result["Total Allocated Capital"],
    )

    print(
        "Remaining Capital:",
        result["Remaining Capital"],
    )

    assert result["Total Allocated Capital"] == 25000
    assert result["Remaining Capital"] == 0

    print("PASS")


    # ---------------------------------------------------------
    # TEST 4
    # Capital remains unused
    # ---------------------------------------------------------

    candidates = [
        {
            "Candidate": "Candidate A",
            "Maximum Allocation": 8000,
        },
        {
            "Candidate": "Candidate B",
            "Maximum Allocation": 5000,
        },
    ]

    result = allocate_capital(
        usable_capital=25000,
        candidates=candidates,
    )

    print("\nTEST 4 — UNUSED CAPITAL")
    print("-----------------------")

    print(
        "Total Allocated:",
        result["Total Allocated Capital"],
    )

    print(
        "Remaining Capital:",
        result["Remaining Capital"],
    )

    assert result["Total Allocated Capital"] == 13000
    assert result["Remaining Capital"] == 12000

    print("PASS — CAPITAL REMAINS UNUSED")


    # ---------------------------------------------------------
    # TEST 5
    # No candidates
    # ---------------------------------------------------------

    result = allocate_capital(
        usable_capital=25000,
        candidates=[],
    )

    print("\nTEST 5 — NO CANDIDATES")
    print("----------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CAPITAL_NOT_ALLOCATED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6
    # Negative candidate allocation
    # ---------------------------------------------------------

    candidates = [
        {
            "Candidate": "Candidate A",
            "Maximum Allocation": -5000,
        }
    ]

    result = allocate_capital(
        usable_capital=25000,
        candidates=candidates,
    )

    print("\nTEST 6 — NEGATIVE ALLOCATION")
    print("----------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "CAPITAL_NOT_ALLOCATED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.6.3 MULTI-CANDIDATE ALLOCATION TEST: PASS")
    print("CAPITAL LIMIT RESPECTED")
    print("MULTIPLE CANDIDATES SUPPORTED")
    print("UNUSED CAPITAL PRESERVED")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()