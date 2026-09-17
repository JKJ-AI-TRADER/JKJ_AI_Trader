"""
JKJ AI Trader
V12.3 — NIFTY Option Movement → Storage Integration Test

Purpose:
Verify that a recorded NIFTY option observation can be
passed directly from the Movement Recorder to CSV Storage.

This test does NOT:
- connect to Zerodha
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify main.py
"""

import csv
import os

from modules.nifty_option_movement_recorder import (
    record_option_observation,
)

import modules.nifty_option_observation_storage as storage


def make_observation():
    return {
        "trading_symbol": "NIFTY2692223200CE",
        "underlying": "NIFTY",
        "expiry": "2026-09-22",
        "strike": 23200.0,
        "option_type": "CE",
        "current_price": 181.95,
        "volume": 151587215,
        "open_interest": 4349215,
        "nifty_spot_price": 23217.6,
        "timestamp": "2026-09-16T11:01:20",
    }


def test_recorder_to_storage():
    observation = record_option_observation(
        **make_observation()
    )

    assert observation["Status"] == "RECORDED"

    storage_result = storage.save_option_observation(
        observation
    )

    assert storage_result["Status"] == "SAVED"
    assert os.path.isfile(storage.OBSERVATION_FILE)

    with open(
        storage.OBSERVATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["Trading Symbol"] == "NIFTY2692223200CE"
    assert rows[0]["Underlying"] == "NIFTY"
    assert rows[0]["Option Type"] == "CE"
    assert float(rows[0]["Strike"]) == 23200.0
    assert float(rows[0]["Current Price"]) == 181.95
    assert float(rows[0]["NIFTY Spot Price"]) == 23217.6

    print("PASS: Movement Recorder → Storage integration works.")


def cleanup():
    if os.path.isfile(storage.OBSERVATION_FILE):
        os.remove(storage.OBSERVATION_FILE)

    print("PASS: Integration test CSV cleaned up.")


def run_all_tests():
    print(
        "\nJKJ AI Trader — "
        "V12.3 Movement Recorder → Storage Test"
    )
    print("=" * 65)

    try:
        test_recorder_to_storage()
    finally:
        cleanup()

    print("\n" + "=" * 65)
    print(
        "V12.3 MOVEMENT RECORDER → STORAGE: PASS"
    )
    print("=" * 65)


if __name__ == "__main__":
    run_all_tests()