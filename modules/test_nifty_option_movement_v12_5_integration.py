"""
JKJ AI Trader
V12.5 End-to-End Integration Test

Flow:
V12.4 ANALYZED
    ↓
V12.5 Stage 1 — Direction
    ↓
V12.5 Stage 2 — Volume/OI
    ↓
V12.5 Stage 3 — Relationship
    ↓
V12.5 Stage 4 — Combined Interpretation

This test does NOT:
- make BUY/SELL decisions
- place orders
- modify main.py
"""

from modules.nifty_option_movement_direction import (
    interpret_movement_direction,
)

from modules.nifty_option_volume_oi_behavior import (
    interpret_volume_oi_behavior,
)

from modules.nifty_option_movement_relationship import (
    interpret_movement_relationship,
)

from modules.nifty_option_combined_interpretation import (
    combine_movement_interpretation,
)


def test_v12_5_end_to_end():

    analyzed_movement = {
        "Status": "ANALYZED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",

        "Previous Timestamp": "2026-09-17T04:48:58",
        "Current Timestamp": "2026-09-17T04:49:08",

        "Previous Option Price": 141.10,
        "Current Option Price": 140.00,
        "Option Price Change": -1.10,
        "Option Price Change %": -0.7796,

        "Previous NIFTY Spot": 23300.75,
        "Current NIFTY Spot": 23301.10,
        "NIFTY Spot Change": 0.35,
        "NIFTY Spot Change %": 0.0015,

        "Previous Volume": 60707530,
        "Current Volume": 60809970,
        "Volume Change": 102440,

        "Previous Open Interest": 7208890,
        "Current Open Interest": 7208890,
        "Open Interest Change": 0,
    }

    # Stage 1
    direction_result = interpret_movement_direction(
        analyzed_movement
    )

    assert direction_result["Status"] == "INTERPRETED"
    assert direction_result["Option Direction"] == "DOWN"
    assert direction_result["NIFTY Direction"] == "UP"

    # Stage 2
    volume_oi_result = interpret_volume_oi_behavior(
        analyzed_movement
    )

    assert volume_oi_result["Status"] == "INTERPRETED"
    assert volume_oi_result["Volume Behaviour"] == "INCREASING"
    assert volume_oi_result["Open Interest Behaviour"] == "UNCHANGED"

    # Stage 3
    relationship_result = interpret_movement_relationship(
        direction_result
    )

    assert relationship_result["Status"] == "INTERPRETED"
    assert relationship_result["Movement Relationship"] == "DIVERGING"

    # Stage 4
    combined_result = combine_movement_interpretation(
        direction_result,
        volume_oi_result,
        relationship_result,
    )

    assert combined_result["Status"] == "INTERPRETED"
    assert combined_result["Option Direction"] == "DOWN"
    assert combined_result["NIFTY Direction"] == "UP"
    assert combined_result["Movement Relationship"] == "DIVERGING"
    assert combined_result["Volume Behaviour"] == "INCREASING"
    assert combined_result["Open Interest Behaviour"] == "UNCHANGED"

    print("\nV12.5 END-TO-END INTERPRETATION")
    print("--------------------------------")
    print("Trading Symbol:", combined_result["Trading Symbol"])
    print("Option Direction:", combined_result["Option Direction"])
    print("NIFTY Direction:", combined_result["NIFTY Direction"])
    print(
        "Movement Relationship:",
        combined_result["Movement Relationship"],
    )
    print("Volume Behaviour:", combined_result["Volume Behaviour"])
    print(
        "Open Interest Behaviour:",
        combined_result["Open Interest Behaviour"],
    )
    print("--------------------------------")
    print("V12.5 END-TO-END INTEGRATION: PASS")


if __name__ == "__main__":
    test_v12_5_end_to_end()