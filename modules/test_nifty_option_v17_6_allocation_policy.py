"""
JKJ AI Trader
V17.6.4 — Allocation Policy Test

NO LIVE ORDER.
"""

from modules.nifty_option_v17_6_allocation_policy import (
    validate_allocation_policy,
)


def main():

    print("=" * 60)
    print("JKJ V17.6.4")
    print("ALLOCATION POLICY & PRIORITY VALIDATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1 — Normal policy
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=6,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    print("\nTEST 1 — NORMAL POLICY")
    print("----------------------")

    print("Status:", result["Status"])
    print("Maximum Positions:",
          result["Maximum Positions"])
    print("Maximum Capital Per Candidate:",
          result["Maximum Capital Per Candidate"])
    print("Minimum Candidate Allocation:",
          result["Minimum Candidate Allocation"])
    print("Priority Source:",
          result["Priority Source"])
    print("Automatic Ranking:",
          result["Automatic Ranking"])

    assert result["Status"] == "ALLOCATION_POLICY_VALIDATED"
    assert result["Maximum Positions"] == 6
    assert result["Maximum Capital Per Candidate"] == 20000
    assert result["Minimum Candidate Allocation"] == 5000
    assert result["Automatic Ranking"] is False

    print("PASS")


    # ---------------------------------------------------------
    # TEST 2 — One position
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=1,
        max_capital_per_candidate=25000,
        minimum_candidate_allocation=5000,
    )

    print("\nTEST 2 — SINGLE POSITION")
    print("------------------------")

    print("Status:", result["Status"])

    assert result["Status"] == "ALLOCATION_POLICY_VALIDATED"

    print("PASS")


    # ---------------------------------------------------------
    # TEST 3 — Minimum equals maximum
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=3,
        max_capital_per_candidate=10000,
        minimum_candidate_allocation=10000,
    )

    print("\nTEST 3 — MINIMUM EQUALS MAXIMUM")
    print("--------------------------------")

    print("Status:", result["Status"])

    assert result["Status"] == "ALLOCATION_POLICY_VALIDATED"

    print("PASS")


    # ---------------------------------------------------------
    # TEST 4 — Minimum exceeds maximum
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=6,
        max_capital_per_candidate=10000,
        minimum_candidate_allocation=15000,
    )

    print("\nTEST 4 — MINIMUM EXCEEDS MAXIMUM")
    print("---------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "ALLOCATION_POLICY_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 5 — Invalid maximum positions
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=0,
        max_capital_per_candidate=20000,
        minimum_candidate_allocation=5000,
    )

    print("\nTEST 5 — INVALID MAXIMUM POSITIONS")
    print("----------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "ALLOCATION_POLICY_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # TEST 6 — Invalid maximum capital
    # ---------------------------------------------------------

    result = validate_allocation_policy(
        max_positions=6,
        max_capital_per_candidate=0,
        minimum_candidate_allocation=5000,
    )

    print("\nTEST 6 — INVALID MAXIMUM CAPITAL")
    print("--------------------------------")

    print("Status:", result["Status"])
    print("Reason:", result["Reason"])

    assert result["Status"] == "ALLOCATION_POLICY_BLOCKED"

    print("PASS — SAFELY BLOCKED")


    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("V17.6.4 ALLOCATION POLICY TEST: PASS")
    print("POLICY VALIDATED")
    print("NO AUTOMATIC RANKING")
    print("NO LIVE ORDER PLACED")
    print("=" * 60)


if __name__ == "__main__":
    main()