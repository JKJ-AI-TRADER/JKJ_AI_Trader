"""
JKJ AI Trader
NIFTY Option Observation Storage — Stage 2 Test

Purpose:
Test CSV storage of validated NIFTY option observations.

This test does NOT:
- connect to Zerodha
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify main.py
"""

import os

import modules.nifty_option_observation_storage as storage


def make_valid_observation():
    return {
        "Status": "RECORDED",
        "Trading Symbol": "NIFTY2692223200CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23200.0,
        "Option Type": "CE",
        "Current Price": 181.95,
        "NIFTY Spot Price": 23217.6,
        "Volume": 151587215,
        "Open Interest": 4349215,
        "Timestamp": "2026-09-16T11:01:20",
    }


def test_valid_observation():
    result = storage.save_option_observation(
        make_valid_observation()
    )

    assert result["Status"] == "SAVED"
    assert os.path.isfile(storage.OBSERVATION_FILE)

    print("PASS: Valid observation is saved.")


def test_invalid_input():
    result = storage.save_option_observation(None)

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid input is rejected.")


def test_unrecorded_observation():
    observation = make_valid_observation()
    observation["Status"] = "READY"

    result = storage.save_option_observation(
        observation
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Unrecorded observation is rejected.")


def test_csv_header():
    with open(
        storage.OBSERVATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        header = file.readline().strip()

    expected_header = ",".join(
        storage.FIELDNAMES
    )

    assert header == expected_header

    print("PASS: CSV header is correct.")


def test_cleanup():
    if os.path.isfile(storage.OBSERVATION_FILE):
        os.remove(storage.OBSERVATION_FILE)

    assert not os.path.exists(
        storage.OBSERVATION_FILE
    )

    print("PASS: Test CSV file cleaned up.")


def run_all_tests():
    print(
        "\nJKJ AI Trader — "
        "NIFTY Option Observation Storage Tests"
    )
    print("=" * 60)

    test_valid_observation()
    test_invalid_input()
    test_unrecorded_observation()
    test_csv_header()
    test_cleanup()

    print("\n" + "=" * 60)
    print(
        "NIFTY OPTION OBSERVATION STORAGE TESTS: PASS"
    )
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()