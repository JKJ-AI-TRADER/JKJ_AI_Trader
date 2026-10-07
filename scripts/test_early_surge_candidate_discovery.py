"""
JKJ AI Trader
V21.2.18.2 - Early Surge Candidate Discovery Tests

Synthetic/local tests only.
No Zerodha connection.
No live orders.
No paper trades.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.nifty_option_early_surge_candidate_discovery import (
    discover_early_surge_candidates,
)


def make_candidate(
    symbol,
    option_type,
    strike,
    movement,
    daily_change,
    early_candidate=True,
):
    return {
        "Trading Symbol": symbol,
        "Option Type": option_type,
        "Strike": strike,
        "Expiry": "2026-09-29",
        "Previous Close": 100.0,
        "9:15 Price": 100.0,
        "Initial Price": 100.0 + movement,
        "Latest Price": 100.0 + movement,
        "Movement Since 9:15 %": movement,
        "9:15 Movement Level": "EARLY_MOVEMENT",
        "Daily Change %": daily_change,
        "Window Change %": 0.0,
        "Acceleration %": 0.0,
        "Initial Classification": "NORMAL",
        "Final Classification": "NORMAL",
        "Reversal Up": False,
        "Upward Acceleration": False,
        "Early Surge Candidate": early_candidate,
    }


def make_scanner(candidates):
    return {
        "Status": "SCAN_COMPLETE",
        "NIFTY Spot": 23200.0,
        "Expiry": "2026-09-29",
        "Universe Count": len(candidates),
        "Results": candidates,
        "Candidates": candidates,
        "Live Order": False,
        "Paper Trade": False,
    }


def make_history(symbol, prices):
    history = []

    for number, price in enumerate(prices, start=1):
        history.append(
            {
                "Status": "RECORDED",
                "Trading Symbol": symbol,
                "Observation Number": number,
                "Timestamp": (
                    f"2026-09-28T10:00:{number:02d}"
                ),
                "Current Price": float(price),
            }
        )

    return history


def run_test_1():
    """
    Test 1:
    Developing movement without observation history.
    """

    candidate = make_candidate(
        "NIFTY26SEP23200PE",
        "PE",
        23200,
        4.5,
        8.0,
    )

    result = discover_early_surge_candidates(
        make_scanner([candidate])
    )

    assert result["Status"] == (
        "EARLY_SURGE_DISCOVERY_COMPLETE"
    )

    assert result["Discovery Candidate Count"] == 1

    item = result["Candidates"][0]

    assert item["State"] in {
        "DEVELOPING",
        "WATCH",
    }

    assert item["Live Order"] is False
    assert item["Paper Trade"] is False

    print("TEST 1 PASS - Developing candidate")


def run_test_2():
    """
    Test 2:
    Nearby strikes confirm movement.
    """

    candidates = [
        make_candidate(
            "NIFTY26SEP23200PE",
            "PE",
            23200,
            5.0,
            10.0,
        ),
        make_candidate(
            "NIFTY26SEP23250PE",
            "PE",
            23250,
            6.0,
            11.0,
        ),
        make_candidate(
            "NIFTY26SEP23300PE",
            "PE",
            23300,
            5.5,
            10.5,
        ),
    ]

    result = discover_early_surge_candidates(
        make_scanner(candidates)
    )

    assert result["Discovery Candidate Count"] == 3

    first = result["Candidates"][0]

    assert first["Supporting Strike Count"] >= 2

    print(
        "TEST 2 PASS - Multi-strike movement detected"
    )


def run_test_3():
    """
    Test 3:
    Existing analyzer identifies acceleration.
    """

    symbol = "NIFTY26SEP23200PE"

    candidate = make_candidate(
        symbol,
        "PE",
        23200,
        8.0,
        15.0,
    )

    history = make_history(
        symbol,
        [
            100,
            101,
            103,
            107,
            113,
        ],
    )

    observation_result = {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",
        "Observation Count": 5,
        "Movement Intervals": 4,
        "Interval Seconds": 10,
        "Contract Count": 1,
        "Observations By Contract": {
            ("NIFTY", symbol): history
        },
        "Latest Observations": {},
        "Live Order": False,
        "Paper Trade": False,
    }

    result = discover_early_surge_candidates(
        make_scanner([candidate]),
        observation_result,
    )

    item = result["Candidates"][0]

    assert item["Observation Status"] == (
        "ANALYSIS_COMPLETE"
    )

    assert item["Analyzer Overall State"] is not None

    assert item["Live Order"] is False
    assert item["Paper Trade"] is False

    print(
        "TEST 3 PASS - Analyzer integrated"
    )


def run_test_4():
    """
    Test 4:
    Extended movement is not automatically treated
    as acceleration.
    """

    candidate = make_candidate(
        "NIFTY26SEP22500PE",
        "PE",
        22500,
        55.0,
        70.0,
    )

    result = discover_early_surge_candidates(
        make_scanner([candidate])
    )

    item = result["Candidates"][0]

    assert item["State"] == "EXTENDED"

    print(
        "TEST 4 PASS - Extended move handled separately"
    )


def run_test_5():
    """
    Test 5:
    Safety flags must remain false.
    """

    candidates = [
        make_candidate(
            "NIFTY26SEP23200CE",
            "CE",
            23200,
            5.0,
            8.0,
        )
    ]

    result = discover_early_surge_candidates(
        make_scanner(candidates)
    )

    assert result["Live Order"] is False
    assert result["Paper Trade"] is False

    for item in result["Candidates"]:
        assert item["Live Order"] is False
        assert item["Paper Trade"] is False

    print(
        "TEST 5 PASS - Trading safety flags preserved"
    )


def main():
    print()
    print("=" * 60)
    print("JKJ V21.2.18.2 EARLY SURGE DISCOVERY TEST")
    print("=" * 60)
    print()

    run_test_1()
    run_test_2()
    run_test_3()
    run_test_4()
    run_test_5()

    print()
    print("=" * 60)
    print("ALL V21.2.18.2 TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
