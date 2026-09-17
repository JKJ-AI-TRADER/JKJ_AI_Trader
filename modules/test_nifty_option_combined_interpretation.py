"""
JKJ AI Trader
Test — NIFTY Option Combined Interpretation V12.5 Stage 4
"""

from modules.nifty_option_combined_interpretation import (
    combine_movement_interpretation,
)


def build_direction_result():
    return {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": "DOWN",
        "NIFTY Direction": "UP",
    }


def build_volume_oi_result():
    return {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Volume Behaviour": "INCREASING",
        "Open Interest Behaviour": "UNCHANGED",
    }


def build_relationship_result():
    return {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": "DOWN",
        "NIFTY Direction": "UP",
        "Movement Relationship": "DIVERGING",
    }


def test_valid_combined_interpretation():
    result = combine_movement_interpretation(
        build_direction_result(),
        build_volume_oi_result(),
        build_relationship_result(),
    )

    assert result["Status"] == "INTERPRETED"
    assert result["Option Direction"] == "DOWN"
    assert result["NIFTY Direction"] == "UP"
    assert result["Movement Relationship"] == "DIVERGING"
    assert result["Volume Behaviour"] == "INCREASING"
    assert result["Open Interest Behaviour"] == "UNCHANGED"


def test_identity_mismatch():
    volume_oi_result = build_volume_oi_result()
    volume_oi_result["Trading Symbol"] = "DIFFERENT_SYMBOL"

    result = combine_movement_interpretation(
        build_direction_result(),
        volume_oi_result,
        build_relationship_result(),
    )

    assert result["Status"] == "REJECTED"


def test_invalid_direction_status():
    direction_result = build_direction_result()
    direction_result["Status"] = "REJECTED"

    result = combine_movement_interpretation(
        direction_result,
        build_volume_oi_result(),
        build_relationship_result(),
    )

    assert result["Status"] == "REJECTED"


def test_invalid_volume_oi_status():
    volume_oi_result = build_volume_oi_result()
    volume_oi_result["Status"] = "REJECTED"

    result = combine_movement_interpretation(
        build_direction_result(),
        volume_oi_result,
        build_relationship_result(),
    )

    assert result["Status"] == "REJECTED"


def test_invalid_relationship_status():
    relationship_result = build_relationship_result()
    relationship_result["Status"] = "REJECTED"

    result = combine_movement_interpretation(
        build_direction_result(),
        build_volume_oi_result(),
        relationship_result,
    )

    assert result["Status"] == "REJECTED"


def test_missing_direction_field():
    direction_result = build_direction_result()
    del direction_result["Option Direction"]

    result = combine_movement_interpretation(
        direction_result,
        build_volume_oi_result(),
        build_relationship_result(),
    )

    assert result["Status"] == "REJECTED"


def test_missing_volume_oi_field():
    volume_oi_result = build_volume_oi_result()
    del volume_oi_result["Volume Behaviour"]

    result = combine_movement_interpretation(
        build_direction_result(),
        volume_oi_result,
        build_relationship_result(),
    )

    assert result["Status"] == "REJECTED"


def test_missing_relationship_field():
    relationship_result = build_relationship_result()
    del relationship_result["Movement Relationship"]

    result = combine_movement_interpretation(
        build_direction_result(),
        build_volume_oi_result(),
        relationship_result,
    )

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_combined_interpretation()
    test_identity_mismatch()
    test_invalid_direction_status()
    test_invalid_volume_oi_status()
    test_invalid_relationship_status()
    test_missing_direction_field()
    test_missing_volume_oi_field()
    test_missing_relationship_field()

    print("V12.5 Stage 4 Combined Interpretation: PASS")