from modules.nifty_option_risk_trade_quality_historical_validation import (
    validate_historical_risk_trade_quality,
)


def build_observation(
    timestamp,
    option_price,
    nifty_price,
    volume,
    oi,
    status="RECORDED",
):
    return {
        "Status": status,
        "Timestamp": timestamp,
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Current Price": option_price,
        "NIFTY Spot Price": nifty_price,
        "Volume": volume,
        "Open Interest": oi,
    }


def test_insufficient_observations():
    observations = [
        build_observation("10:00:00", 100, 23000, 1000, 500),
        build_observation("10:01:00", 101, 23010, 1100, 500),
        build_observation("10:02:00", 102, 23020, 1200, 500),
    ]

    result = validate_historical_risk_trade_quality(observations)

    print("INSUFFICIENT RESULT:", result)

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"


def test_supported_strong_trade_quality():
    observations = [
        build_observation("10:00:00", 100, 23000, 1000, 500),
        build_observation("10:01:00", 101, 23010, 1100, 510),
        build_observation("10:02:00", 102, 23020, 1200, 520),
        build_observation("10:03:00", 103, 23030, 1300, 530),
    ]

    result = validate_historical_risk_trade_quality(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Observation Count"] == 4
    assert result["Movement Count"] == 3
    assert result["Option Direction"] == "UP"
    assert result["Momentum Persistence"] == "PERSISTENT"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "MOVING_TOGETHER"
    assert result["Momentum Context"] == "SUPPORTED"
    assert result["Opportunity Classification"] == "SUPPORTED_OPPORTUNITY"
    assert result["Opportunity Strength"] == "STRONG"
    assert result["Risk Classification"] == "LOWER_RISK_CONTEXT"
    assert result["Trade Quality"] == "HIGH_QUALITY_CONTEXT"


def test_conflicting_trade_quality():
    observations = [
        build_observation("10:00:00", 100, 23030, 1000, 500),
        build_observation("10:01:00", 101, 23020, 1100, 510),
        build_observation("10:02:00", 102, 23010, 1200, 520),
        build_observation("10:03:00", 103, 23000, 1300, 530),
    ]

    result = validate_historical_risk_trade_quality(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Option Direction"] == "UP"
    assert result["Momentum Persistence"] == "PERSISTENT"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "DIVERGING"
    assert result["Momentum Context"] == "CONTEXT_CONFLICT"
    assert result["Opportunity Classification"] == "CONTEXT_CONFLICT"
    assert result["Opportunity Strength"] == "WEAK"
    assert result["Risk Classification"] == "HIGHER_RISK_CONTEXT"
    assert result["Trade Quality"] == "LOW_QUALITY_CONTEXT"


def test_invalid_observation():
    observations = [
        build_observation("10:00:00", 100, 23000, 1000, 500),
        build_observation("10:01:00", 101, 23010, 1100, 500),
        build_observation("10:02:00", 102, 23020, 1200, 500),
        build_observation(
            "10:03:00",
            103,
            23030,
            1300,
            500,
            status="INVALID",
        ),
    ]

    result = validate_historical_risk_trade_quality(observations)

    assert result["Status"] == "REJECTED"


def test_invalid_input():
    result = validate_historical_risk_trade_quality(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_insufficient_observations()
    test_supported_strong_trade_quality()
    test_conflicting_trade_quality()
    test_invalid_observation()
    test_invalid_input()

    print(
        "V12.9 Stage 4 Historical Risk & Trade Quality Validation: PASS"
    )