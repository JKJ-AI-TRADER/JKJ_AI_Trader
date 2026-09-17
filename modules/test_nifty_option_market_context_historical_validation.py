"""
JKJ AI Trader
Test — NIFTY Option Market Context Historical Validation — V12.7 Stage 4
"""

from modules.nifty_option_market_context_historical_validation import (
    validate_historical_market_context,
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

    result = validate_historical_market_context(
        observations
    )

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"


def test_persistent_supported_context():

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

    result = validate_historical_market_context(
        observations
    )

    assert result["Status"] == "VALIDATED"
    assert result["Observation Count"] == 4
    assert result["Movement Count"] == 3
    assert result["Option Direction"] == "UP"
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "MOVING_TOGETHER"
    assert result["Momentum Context"] == "SUPPORTED"


def test_persistent_diverging_context():

    observations = [
        build_observation(
            "2026-09-01T10:00:00",
            100.0,
            23303.0,
            1000,
            5000,
        ),
        build_observation(
            "2026-09-01T10:01:00",
            102.0,
            23302.0,
            1100,
            5000,
        ),
        build_observation(
            "2026-09-01T10:02:00",
            104.0,
            23301.0,
            1200,
            5000,
        ),
        build_observation(
            "2026-09-01T10:03:00",
            106.0,
            23300.0,
            1300,
            5000,
        ),
    ]

    result = validate_historical_market_context(
        observations
    )

    assert result["Status"] == "VALIDATED"
    assert result["Option Direction"] == "UP"
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "DIVERGING"
    assert result["Momentum Context"] == "CONTEXT_CONFLICT"


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

    result = validate_historical_market_context(
        observations
    )

    assert result["Status"] == "REJECTED"


def test_invalid_input():

    result = validate_historical_market_context(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_insufficient_observations()
    test_persistent_supported_context()
    test_persistent_diverging_context()
    test_invalid_observation()
    test_invalid_input()

    print(
        "V12.7 Stage 4 Historical Market Context Validation: PASS"
    )