"""
JKJ AI Trader
V16.1 — Real-Market to Paper Entry Validation Test

Tests:
    1. Strong real-market-shaped setup -> paper trade opened
    2. Developing setup -> no paper trade
    3. Conflicting setup -> no paper trade
    4. Insufficient observations -> rejected safely

Wisdom Before Wealth.
"""

from modules.nifty_option_v16_real_market_paper_validation import (
    validate_real_market_paper_entry,
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


def strong_observations():
    return [
        make_observation("09:15", 100, 23000, 1000, 500),
        make_observation("09:20", 101, 23010, 1100, 510),
        make_observation("09:25", 102, 23020, 1200, 520),
        make_observation("09:30", 103, 23030, 1300, 530),
    ]


def developing_observations():
    return [
        make_observation("09:15", 100, 23000, 1000, 500),
        make_observation("09:20", 101, 23010, 1100, 510),
        make_observation("09:25", 102, 23020, 1200, 520),
        make_observation("09:30", 103, 23030, 1200, 530),
    ]


def conflicting_observations():
    return [
        make_observation("09:15", 100, 23030, 1000, 500),
        make_observation("09:20", 101, 23020, 1100, 510),
        make_observation("09:25", 102, 23010, 1200, 520),
        make_observation("09:30", 103, 23000, 1300, 530),
    ]


def test_strong_setup():
    result = validate_real_market_paper_entry(
        strong_observations(),
        quantity=75,
        trade_id="V16-TEST-001",
    )
    
    assert result["Status"] == "PAPER_TRADE_OPENED"
    assert result["Market Validation"] == "PASSED"
    assert result["Paper Trade Permission"] == "PERMITTED"

    trade = result["Paper Trade Result"]["Trade"]

    assert trade["Status"] == "OPEN"
    assert trade["Entry Price"] == 103
    assert trade["Stop Loss"] == 100
    assert trade["Target"] == 106

    paper_qualification = result["Paper Qualification"]
    assert paper_qualification["Target 1"] == 106
    assert paper_qualification["Target 2"] == 109
    assert paper_qualification["Target 3"] == 112

    print("Strong Setup → Paper Trade Opened: PASS")


def test_developing_setup():
    result = validate_real_market_paper_entry(
        developing_observations(),
        quantity=75,
        trade_id="V16-TEST-002",
    )

    assert result["Status"] == "NOT_QUALIFIED"

    print("Developing Setup → No Paper Trade: PASS")


def test_conflicting_setup():
    result = validate_real_market_paper_entry(
        conflicting_observations(),
        quantity=75,
        trade_id="V16-TEST-003",
    )

    assert result["Status"] == "NOT_QUALIFIED"

    print("Conflicting Setup → No Paper Trade: PASS")


def test_insufficient_observations():
    observations = strong_observations()[:3]

    result = validate_real_market_paper_entry(
        observations,
        quantity=75,
        trade_id="V16-TEST-004",
    )

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"

    print("Insufficient Observations → Safe Stop: PASS")


if __name__ == "__main__":
    test_strong_setup()
    test_developing_setup()
    test_conflicting_setup()
    test_insufficient_observations()

    print()
    print(
        "V16.1 Real-Market to Paper Entry Validation: "
        "ALL TESTS PASSED"
    )
