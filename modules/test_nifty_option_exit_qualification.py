from modules.nifty_option_exit_qualification import (
    evaluate_exit_qualification,
)


def build_target_data():
    return {
        "Status": "TARGETS_VALIDATED",
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

        "Target 1": 111,
        "Target 2": 117,
        "Target 3": 123,
    }


def test_supported_exit_structure():
    result = evaluate_exit_qualification(
        build_target_data()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Exit Structure"] == (
        "EXIT_STRUCTURE_SUPPORTED"
    )

    assert result["Risk Reward 1"] == 1
    assert result["Risk Reward 2"] == 2
    assert result["Risk Reward 3"] == 3


def test_developing_exit_structure():
    data = build_target_data()
    data["Entry Qualification"] = "ENTRY_DEVELOPING"
    data["Entry Risk Context"] = "DEVELOPING_RISK_CONTEXT"
    data["Stop-Loss Context"] = "STOP_DEVELOPING"

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "EVALUATED"
    assert result["Exit Structure"] == (
        "EXIT_STRUCTURE_DEVELOPING"
    )


def test_not_supported_entry():
    data = build_target_data()
    data["Entry Qualification"] = "ENTRY_NOT_QUALIFIED"

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "EVALUATED"
    assert result["Exit Structure"] == (
        "EXIT_STRUCTURE_NOT_SUPPORTED"
    )


def test_invalid_targets():
    data = build_target_data()
    data["Target 2"] = 108

    result = evaluate_exit_qualification(data)

    assert result["Status"] == (
        "EXIT_STRUCTURE_NOT_SUPPORTED"
    )


def test_invalid_stop():
    data = build_target_data()
    data["Stop Price"] = 110

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "REJECTED"


def test_invalid_stop_distance():
    data = build_target_data()
    data["Stop Distance"] = 0

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "REJECTED"


def test_invalid_status():
    data = build_target_data()
    data["Status"] = "INVALID"

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "REJECTED"


def test_missing_field():
    data = build_target_data()
    del data["Target 3"]

    result = evaluate_exit_qualification(data)

    assert result["Status"] == "REJECTED"


def test_invalid_input():
    result = evaluate_exit_qualification(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_supported_exit_structure()
    test_developing_exit_structure()
    test_not_supported_entry()
    test_invalid_targets()
    test_invalid_stop()
    test_invalid_stop_distance()
    test_invalid_status()
    test_missing_field()
    test_invalid_input()

    print("V14.5 Risk/Reward + Exit Qualification: PASS")