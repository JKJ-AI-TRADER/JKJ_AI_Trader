"""
JKJ AI Trader
V13–V14 Historical Decision & Risk Validation Test

Tests:
1. Strong supported setup
2. Developing setup
3. Conflicting setup
4. Insufficient observations
"""

from modules.nifty_option_v13_v14_historical_validation import (
    validate_historical_v13_v14,
)


def make_observation(
    timestamp,
    option_price,
    nifty_price,
    volume,
    open_interest,
):
    return {
        "Status": "RECORDED",
        "Trading Symbol": "NIFTY26SEP25000CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 25000,
        "Option Type": "CE",
        "Timestamp": timestamp,
        "Current Price": option_price,
        "NIFTY Spot Price": nifty_price,
        "Volume": volume,
        "Open Interest": open_interest,
    }


def test_strong_supported_setup():
    observations = [
        make_observation("09:15", 100, 23000, 1000, 500),
        make_observation("09:20", 101, 23010, 1100, 510),
        make_observation("09:25", 102, 23020, 1200, 520),
        make_observation("09:30", 103, 23030, 1300, 530),
    ]

    result = validate_historical_v13_v14(observations)

    assert result["Status"] == "VALIDATED"
    assert result["Option Direction"] == "UP"
    assert result["Momentum Persistence"] == "PERSISTENT"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "MOVING_TOGETHER"
    assert result["Momentum Context"] == "SUPPORTED"
    assert (
        result["Opportunity Classification"]
        == "SUPPORTED_OPPORTUNITY"
    )
    assert result["Opportunity Strength"] == "STRONG"
    assert result["Risk Classification"] == "LOWER_RISK_CONTEXT"
    assert result["Trade Quality"] == "HIGH_QUALITY_CONTEXT"

    assert result["Entry Qualification"] == "ENTRY_QUALIFIED"
    assert (
        result["Entry Risk Context"]
        == "CONTROLLED_RISK_CONTEXT"
    )
    assert result["Stop-Loss Context"] == "STOP_SUPPORTED"

    assert result["Entry Price"] == 103
    assert result["Structural Low"] == 100
    assert result["Stop Price"] == 100
    assert result["Stop Distance"] == 3

    assert result["Target 1"] == 106
    assert result["Target 2"] == 109
    assert result["Target 3"] == 112

    assert result["Risk Reward 1"] == 1
    assert result["Risk Reward 2"] == 2
    assert result["Risk Reward 3"] == 3

    assert (
        result["Exit Structure"]
        == "EXIT_STRUCTURE_SUPPORTED"
    )

    print("Strong Supported Setup: PASS")


def test_developing_setup():
    observations = [
        make_observation("09:15", 100, 23000, 1000, 500),
        make_observation("09:20", 101, 23010, 1100, 510),
        make_observation("09:25", 102, 23020, 1200, 520),
        make_observation("09:30", 103, 23030, 1200, 530),
    ]

    result = validate_historical_v13_v14(observations)

    assert result["Status"] == "VALIDATED_TO_STOP_CONTEXT"
    assert result["Entry Qualification"] == "ENTRY_NOT_QUALIFIED"
    assert result["Entry Risk Context"] == "ELEVATED_RISK_CONTEXT"
    assert result["Stop-Loss Context"] == "STOP_NOT_SUPPORTED"
    assert result["Entry Price"] == 103

    print("Developing Setup: PASS")


def test_conflicting_setup():
    observations = [
        make_observation("09:15", 100, 23030, 1000, 500),
        make_observation("09:20", 101, 23020, 1100, 510),
        make_observation("09:25", 102, 23010, 1200, 520),
        make_observation("09:30", 103, 23000, 1300, 530),
    ]

    result = validate_historical_v13_v14(observations)

    print("Conflicting Result:", result)

    assert result["Status"] == "VALIDATED_TO_STOP_CONTEXT"

    print("Conflicting Setup: PASS")


def test_insufficient_observations():
    observations = [
        make_observation("09:15", 100, 23000, 1000, 500),
        make_observation("09:20", 101, 23010, 1100, 510),
        make_observation("09:25", 102, 23020, 1200, 520),
    ]

    result = validate_historical_v13_v14(observations)

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"

    print("Insufficient Observations: PASS")


if __name__ == "__main__":
    test_strong_supported_setup()
    test_developing_setup()
    test_conflicting_setup()
    test_insufficient_observations()

    print()
    print("V13–V14 Historical Validation: ALL TESTS PASSED")