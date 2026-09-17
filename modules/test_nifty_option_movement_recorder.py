"""
JKJ AI Trader
NIFTY Option Movement Recorder — Stage 1 Test

Purpose:
Test single validated NIFTY option observation recording.

This test does NOT:
- connect to Zerodha
- place orders
- make BUY/SELL decisions
- calculate momentum
- modify main.py
"""


from modules.nifty_option_movement_recorder import (
    record_option_observation,
)


def make_valid_observation():
    return {
        "trading_symbol": "NIFTY2692223200CE",
        "underlying": "NIFTY",
        "expiry": "2026-09-22",
        "strike": 23200.0,
        "option_type": "CE",
        "current_price": 181.95,
        "volume": 151587215,
        "open_interest": 4349215,
        "nifty_spot_price": 23217.6,
        "timestamp": "2026-09-16T11:01:20",
    }


def test_valid_observation():
    result = record_option_observation(
        **make_valid_observation()
    )

    assert result["Status"] == "RECORDED"
    assert result["Trading Symbol"] == "NIFTY2692223200CE"
    assert result["Underlying"] == "NIFTY"
    assert result["Expiry"] == "2026-09-22"
    assert result["Strike"] == 23200.0
    assert result["Option Type"] == "CE"
    assert result["Current Price"] == 181.95
    assert result["NIFTY Spot Price"] == 23217.6

    print("PASS: Valid NIFTY option observation is recorded.")


def test_invalid_symbol():
    data = make_valid_observation()
    data["trading_symbol"] = ""

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid trading symbol is rejected.")


def test_invalid_option_type():
    data = make_valid_observation()
    data["option_type"] = "XX"

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid option type is rejected.")


def test_invalid_price():
    data = make_valid_observation()
    data["current_price"] = 0

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid option price is rejected.")


def test_invalid_nifty_spot():
    data = make_valid_observation()
    data["nifty_spot_price"] = 0

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid NIFTY spot price is rejected.")


def test_negative_volume():
    data = make_valid_observation()
    data["volume"] = -1

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Negative volume is rejected.")


def test_negative_open_interest():
    data = make_valid_observation()
    data["open_interest"] = -1

    result = record_option_observation(**data)

    assert result["Status"] == "REJECTED"

    print("PASS: Negative open interest is rejected.")


def run_all_tests():
    print("\nJKJ AI Trader — NIFTY Option Movement Recorder Tests")
    print("=" * 60)

    test_valid_observation()
    test_invalid_symbol()
    test_invalid_option_type()
    test_invalid_price()
    test_invalid_nifty_spot()
    test_negative_volume()
    test_negative_open_interest()

    print("\n" + "=" * 60)
    print("NIFTY OPTION MOVEMENT RECORDER TESTS: PASS")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()