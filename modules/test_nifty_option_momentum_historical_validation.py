"""
JKJ AI Trader
Test — NIFTY Option Momentum Historical Validation — V12.6 Stage 4
"""

from modules.nifty_option_momentum_historical_validation import (
    validate_historical_momentum,
)


def build_observation(
    timestamp,
    price,
    nifty,
    volume,
    oi,
):
    return {
        "Status": "RECORDED",
        "Trading Symbol": "NIFTYTESTCE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Current Price": price,
        "NIFTY Spot Price": nifty,
        "Volume": volume,
        "Open Interest": oi,
        "Timestamp": timestamp,
    }


def test_insufficient_observations():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23300.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:01:00",
            102.0,
            23301.0,
            1100,
            5000,
        ),
        build_observation(
            "2026-09-01T10:02:00",
            104.0,
            23302.0,
            1200,
            5000,
        ),
    ]

    result = validate_historical_momentum(observations)

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"
    assert result["Observation Count"] == 3


def test_persistent_confirmed():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23300.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:01:00",
            102.0,
            23301.0,
            1100,
            5000,
        ),
        build_observation(
            "2026-09-01T10:02:00",
            104.0,
            23302.0,
            1200,
            5000,
        ),
        build_observation(
            "2026-09-01T10:03:00",
            106.0,
            23303.0,
            1300,
            5000,
        ),
    ]

    result = validate_historical_momentum(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Movement Count"] == 3
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Option Direction"] == "UP"
    assert result["Price Movement Evidence"] is True
    assert result["Volume Evidence"] is True
    assert result["Momentum Confirmation"] == "CONFIRMED"


def test_persistent_partial_confirmation():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23300.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:01:00",
            102.0,
            23301.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:02:00",
            104.0,
            23302.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:03:00",
            106.0,
            23303.0,
            1000,
            5000,
        ),
    ]

    result = validate_historical_momentum(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Option Direction"] == "UP"
    assert result["Volume Evidence"] is False
    assert result["Momentum Confirmation"] == "PARTIALLY_CONFIRMED"


def test_not_persistent():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23300.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:01:00",
            102.0,
            23301.0,
            1100,
            5000,
        ),
        build_observation(
            "2026-09-01T10:02:00",
            101.0,
            23302.0,
            1200,
            5000,
        ),
        build_observation(
            "2026-09-01T10:03:00",
            103.0,
            23303.0,
            1300,
            5000,
        ),
    ]

    result = validate_historical_momentum(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Persistence Status"] == "NOT_PERSISTENT"
    assert result["Momentum Confirmation"] == "NOT_CONFIRMED"


def test_invalid_observation():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23300.0,
            1000,
            5000,
        ),
        {
            "Status": "INVALID",
        },
        build_observation(
            "2026-09-01T10:02:00",
            102.0,
            23302.0,
            1200,
            5000,
        ),
        build_observation(
            "2026-09-01T10:03:00",
            103.0,
            23303.0,
            1300,
            5000,
        ),
    ]

    result = validate_historical_momentum(observations)

    assert result["Status"] == "REJECTED"

    result = validate_historical_momentum(observations)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_insufficient_observations()
    test_persistent_confirmed()
    test_persistent_partial_confirmation()
    test_not_persistent()
    test_invalid_observation()

    print(
        "V12.6 Stage 4 Historical Momentum Validation: PASS"
    )