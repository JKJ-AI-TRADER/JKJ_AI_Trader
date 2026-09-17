"""
JKJ AI Trader
NIFTY Option Movement Analyzer — V12.4 Tests
"""

from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)


def make_observation(
    price=100.0,
    nifty=23000.0,
    volume=1000,
    oi=5000,
    timestamp="2026-09-17T09:30:00",
):
    return {
        "Status": "RECORDED",
        "Trading Symbol": "NIFTY2692223250CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23250.0,
        "Option Type": "CE",
        "Current Price": price,
        "NIFTY Spot Price": nifty,
        "Volume": volume,
        "Open Interest": oi,
        "Timestamp": timestamp,
    }


print("=" * 70)
print("JKJ AI Trader — V12.4 Movement Analyzer Tests")
print("=" * 70)


# Test 1 — valid upward movement
previous = make_observation()
current = make_observation(
    price=110.0,
    nifty=23100.0,
    volume=1500,
    oi=5200,
    timestamp="2026-09-17T09:35:00",
)

result = analyze_option_movement(previous, current)

assert result["Status"] == "ANALYZED"
assert result["Option Price Change"] == 10.0
assert result["Option Price Change %"] == 10.0
assert result["NIFTY Spot Change"] == 100.0
assert result["NIFTY Spot Change %"] > 0
assert result["Volume Change"] == 500
assert result["Open Interest Change"] == 200

print("PASS: Valid movement is calculated.")


# Test 2 — downward movement
previous = make_observation(price=110.0, nifty=23100.0)
current = make_observation(price=100.0, nifty=23000.0)

result = analyze_option_movement(previous, current)

assert result["Status"] == "ANALYZED"
assert result["Option Price Change"] == -10.0
assert result["Option Price Change %"] < 0
assert result["NIFTY Spot Change"] == -100.0

print("PASS: Downward movement is calculated.")


# Test 3 — different trading symbol
previous = make_observation()
current = make_observation()
current["Trading Symbol"] = "NIFTY2692223250PE"

result = analyze_option_movement(previous, current)

assert result["Status"] == "REJECTED"

print("PASS: Different contracts are rejected.")


# Test 4 — invalid previous status
previous = make_observation()
previous["Status"] = "INVALID"
current = make_observation(price=110.0)

result = analyze_option_movement(previous, current)

assert result["Status"] == "REJECTED"

print("PASS: Invalid previous observation is rejected.")


# Test 5 — invalid current status
previous = make_observation()
current = make_observation(price=110.0)
current["Status"] = "INVALID"

result = analyze_option_movement(previous, current)

assert result["Status"] == "REJECTED"

print("PASS: Invalid current observation is rejected.")


print("=" * 70)
print("V12.4 MOVEMENT ANALYZER TESTS: PASS")