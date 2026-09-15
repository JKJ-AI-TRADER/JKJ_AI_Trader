"""
JKJ AI Trader
V12.1 — Observation Record Test Suite

Purpose:
Test the observation-record layer independently.

This test does NOT:
- connect to Zerodha
- place orders
- make BUY/SELL decisions
- modify V1–V11
- modify main.py
"""


from modules.intraday_option_observation_record import (
    create_option_observation_record,
)


def make_valid_observation():
    return {
        "Status": "READY",
        "Data Status": "VALID",
        "Trading Symbol": "NIFTY2691525000PE",
        "Instrument Token": 12125186,
        "Underlying": "NIFTY",
        "Current Price": 1646.35,
        "Open": 1530.95,
        "High": 1652.10,
        "Low": 1482.95,
        "Previous Close": 1549.40,
        "Volume": 30940,
        "Open Interest": 58630,
        "Last Trade Time": "2026-09-15 10:48:45",
        "Observation Timestamp": "2026-09-15T05:35:33",
    }


def test_valid_observation():
    result = create_option_observation_record(
        make_valid_observation()
    )

    assert result["Status"] == "RECORDED"
    assert result["Data Status"] == "VALID"
    assert result["Trading Symbol"] == "NIFTY2691525000PE"
    assert result["Current Price"] == 1646.35

    print("PASS: Valid observation is recorded.")


def test_invalid_input():
    result = create_option_observation_record(
        None
    )

    assert result["Status"] == "INVALID"

    print("PASS: Invalid input is rejected.")


def test_incomplete_observation():
    observation = make_valid_observation()
    observation["Status"] = "INCOMPLETE"

    result = create_option_observation_record(
        observation
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Incomplete observation is rejected.")


def test_stale_observation():
    observation = make_valid_observation()
    observation["Status"] = "STALE"

    result = create_option_observation_record(
        observation
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Stale observation is rejected.")


def test_invalid_data_status():
    observation = make_valid_observation()
    observation["Data Status"] = "INVALID"

    result = create_option_observation_record(
        observation
    )

    assert result["Status"] == "RECORDED"

    print(
        "PASS: Record layer preserves the observer status "
        "without adding new validation."
    )


def run_all_tests():
    print("\nJKJ AI Trader — V12.1 Observation Record Tests")
    print("=" * 55)

    test_valid_observation()
    test_invalid_input()
    test_incomplete_observation()
    test_stale_observation()
    test_invalid_data_status()

    print("\n" + "=" * 55)
    print("V12.1 OBSERVATION RECORD TESTS: PASS")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()