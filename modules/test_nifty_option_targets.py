from modules.nifty_option_targets import (
    evaluate_targets,
)


def build_stop_loss_data():
    return {
        "Status": "STOP_VALIDATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",

        "Option Direction": "UP",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",

        "Entry Price": 105,
        "Stop Price": 99,
        "Stop Distance": 6,
    }


def test_targets():
    result = evaluate_targets(
        build_stop_loss_data()
    )

    assert result["Status"] == "TARGETS_VALIDATED"

    assert result["Entry Price"] == 105
    assert result["Stop Price"] == 99
    assert result["Stop Distance"] == 6

    assert result["Target 1"] == 111
    assert result["Target 2"] == 117
    assert result["Target 3"] == 123


def test_targets_are_increasing():
    result = evaluate_targets(
        build_stop_loss_data()
    )

    assert result["Target 1"] < result["Target 2"]
    assert result["Target 2"] < result["Target 3"]


def test_invalid_stop_status():
    data = build_stop_loss_data()
    data["Status"] = "STOP_REJECTED"

    result = evaluate_targets(data)

    assert result["Status"] == "REJECTED"


def test_stop_above_entry():
    data = build_stop_loss_data()
    data["Stop Price"] = 110

    result = evaluate_targets(data)

    assert result["Status"] == "REJECTED"


def test_invalid_stop_distance():
    data = build_stop_loss_data()
    data["Stop Distance"] = 0

    result = evaluate_targets(data)

    assert result["Status"] == "REJECTED"


def test_missing_field():
    data = build_stop_loss_data()
    del data["Stop Price"]

    result = evaluate_targets(data)

    assert result["Status"] == "REJECTED"


def test_invalid_input():
    result = evaluate_targets(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_targets()
    test_targets_are_increasing()
    test_invalid_stop_status()
    test_stop_above_entry()
    test_invalid_stop_distance()
    test_missing_field()
    test_invalid_input()

    print("V14.4 Targets 1-3: PASS")