"""
JKJ AI Trader
V12.4 Movement Analyzer — V12.3 Integration Test

Purpose:
Verify that two V12.3 RECORDED observations can be passed
directly into the V12.4 Movement Analyzer.

No trading decisions are made.
"""

from modules.nifty_option_movement_recorder import (
    record_option_observation,
)
from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)


def make_observation(
    price,
    nifty_spot,
    volume,
    open_interest,
    timestamp,
):
    return record_option_observation(
        trading_symbol="NIFTY2692223250CE",
        underlying="NIFTY",
        expiry="2026-09-22",
        strike=23250.0,
        option_type="CE",
        current_price=price,
        volume=volume,
        open_interest=open_interest,
        nifty_spot_price=nifty_spot,
        timestamp=timestamp,
    )


print("=" * 70)
print("JKJ AI Trader — V12.3 → V12.4 Integration Test")
print("=" * 70)


previous_observation = make_observation(
    price=149.95,
    nifty_spot=23271.90,
    volume=100000,
    open_interest=4000000,
    timestamp="2026-09-17T09:30:00",
)

current_observation = make_observation(
    price=154.95,
    nifty_spot=23281.90,
    volume=125000,
    open_interest=4050000,
    timestamp="2026-09-17T09:35:00",
)


assert previous_observation["Status"] == "RECORDED"
assert current_observation["Status"] == "RECORDED"

print("PASS: V12.3 observations created.")


movement = analyze_option_movement(
    previous_observation,
    current_observation,
)


assert movement["Status"] == "ANALYZED"
assert movement["Trading Symbol"] == "NIFTY2692223250CE"
assert movement["Option Price Change"] == 5.0
assert movement["NIFTY Spot Change"] == 10.0
assert movement["Volume Change"] == 25000
assert movement["Open Interest Change"] == 50000

print("PASS: V12.3 observations accepted by V12.4.")
print("PASS: Option movement calculated correctly.")
print("PASS: NIFTY spot movement calculated correctly.")
print("PASS: Volume movement calculated correctly.")
print("PASS: Open interest movement calculated correctly.")

print("=" * 70)
print("V12.3 → V12.4 INTEGRATION TEST: PASS")
print("=" * 70)