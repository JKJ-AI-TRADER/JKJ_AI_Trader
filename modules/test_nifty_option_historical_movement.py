"""
JKJ AI Trader
NIFTY Option Historical Movement — V12.4 Stage 3 Tests
"""

import csv
import os

from modules.nifty_option_historical_movement import (
    analyze_historical_movement,
)


TEST_FILE = "test_nifty_option_historical_movement.csv"


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
            "Current Price": "100.0",
            "NIFTY Spot Price": "23000.0",
            "Volume": "1000",
            "Open Interest": "5000",
        },
        {
            "Timestamp": "2026-09-17T09:35:00",
            "Trading Symbol": "NIFTY2692223250CE",
            "Underlying": "NIFTY",
            "Expiry": "2026-09-22",
            "Strike": "23250.0",
            "Option Type": "CE",
            "Current Price": "110.0",
            "NIFTY Spot Price": "23100.0",
            "Volume": "1500",
            "Open Interest": "5200",
        },
        {
            "Timestamp": "2026-09-17T09:40:00",
            "Trading Symbol": "NIFTY2692223250CE",
            "Underlying": "NIFTY",
            "Expiry": "2026-09-22",
            "Strike": "23250.0",
            "Option Type": "CE",
            "Current Price": "120.0",
            "NIFTY Spot Price": "23200.0",
            "Volume": "2000",
            "Open Interest": "5400",
        },
    ]

    with open(TEST_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


print("=" * 70)
print("JKJ AI Trader — V12.4 Historical Movement Tests")
print("=" * 70)


# Test 1 — three observations produce two movements
create_test_csv()

result = analyze_historical_movement(TEST_FILE)

assert result["Status"] == "ANALYZED"
assert result["Observation Count"] == 3
assert result["Movement Count"] == 2

print("PASS: Historical observations are analyzed.")
print("PASS: Three observations produced two movements.")


# Test 2 — first movement
first_movement = result["Movements"][0]

assert first_movement["Option Price Change"] == 10.0
assert first_movement["NIFTY Spot Change"] == 100.0
assert first_movement["Volume Change"] == 500
assert first_movement["Open Interest Change"] == 200

print("PASS: First movement is correct.")


# Test 3 — second movement
second_movement = result["Movements"][1]

assert second_movement["Option Price Change"] == 10.0
assert second_movement["NIFTY Spot Change"] == 100.0
assert second_movement["Volume Change"] == 500
assert second_movement["Open Interest Change"] == 200

print("PASS: Second movement is correct.")


# Test 4 — insufficient data
with open(TEST_FILE, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
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
        ],
    )

    writer.writeheader()

    writer.writerow({
        "Timestamp": "2026-09-17T09:30:00",
        "Trading Symbol": "NIFTY2692223250CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": "23250.0",
        "Option Type": "CE",
        "Current Price": "100.0",
        "NIFTY Spot Price": "23000.0",
        "Volume": "1000",
        "Open Interest": "5000",
    })


result = analyze_historical_movement(TEST_FILE)

assert result["Status"] == "INSUFFICIENT_DATA"
assert result["Movements"] == []

print("PASS: Insufficient observations are handled safely.")


# Cleanup
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

print("PASS: Test CSV cleaned up.")

print("=" * 70)
print("V12.4 HISTORICAL MOVEMENT TESTS: PASS")
print("=" * 70)
