"""
JKJ AI Trader
NIFTY Option Observation Reader — V12.4 Stage 2 Tests
"""

import csv
import os

from modules.nifty_option_observation_reader import (
    read_option_observations,
)


TEST_FILE = "test_nifty_option_observations.csv"


def create_test_csv():
    fieldnames = [
        "Timestamp",
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
        "Current Price",
        "NIFTY Spot Price",
        "Volume",
        "Open Interest",
    ]

    rows = [
        {
            "Timestamp": "2026-09-17T09:30:00",
            "Trading Symbol": "NIFTY2692223250CE",
            "Underlying": "NIFTY",
            "Expiry": "2026-09-22",
            "Strike": "23250.0",
            "Option Type": "CE",
            "Current Price": "149.95",
            "NIFTY Spot Price": "23271.90",
            "Volume": "100000",
            "Open Interest": "4000000",
        },
        {
            "Timestamp": "2026-09-17T09:35:00",
            "Trading Symbol": "NIFTY2692223250CE",
            "Underlying": "NIFTY",
            "Expiry": "2026-09-22",
            "Strike": "23250.0",
            "Option Type": "CE",
            "Current Price": "154.95",
            "NIFTY Spot Price": "23281.90",
            "Volume": "125000",
            "Open Interest": "4050000",
        },
    ]

    with open(TEST_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


print("=" * 70)
print("JKJ AI Trader — V12.4 Observation Reader Tests")
print("=" * 70)


# Test 1 — valid CSV
create_test_csv()

result = read_option_observations(TEST_FILE)

assert result["Status"] == "LOADED"
assert result["Observation Count"] == 2
assert len(result["Observations"]) == 2

print("PASS: Valid observation CSV is loaded.")
print("PASS: Observation count is correct.")


# Test 2 — verify first observation
first = result["Observations"][0]

assert first["Trading Symbol"] == "NIFTY2692223250CE"
assert first["Option Type"] == "CE"
assert first["Current Price"] == "149.95"

print("PASS: Observation fields are read correctly.")


# Test 3 — missing file
missing_file = "file_that_does_not_exist_v12_4.csv"

result = read_option_observations(missing_file)

assert result["Status"] == "REJECTED"
assert result["Observations"] == []

print("PASS: Missing observation file is handled safely.")


# Cleanup
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

print("PASS: Test CSV cleaned up.")

print("=" * 70)
print("V12.4 OBSERVATION READER TESTS: PASS")
print("=" * 70)