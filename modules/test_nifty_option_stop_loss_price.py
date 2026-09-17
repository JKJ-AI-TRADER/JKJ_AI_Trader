from modules.nifty_option_stop_loss_price import (
    evaluate_stop_loss_price,
)


def build_stop_loss_context():
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",

        "Option Direction": "UP",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Risk Classification": "LOWER_RISK_CONTEXT",
        "Trade Quality": "HIGH_QUALITY_CONTEXT",

        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
    }


def test_valid_stop_loss():
    result = evaluate_stop_loss_price(
        build_stop_loss_context(),
        105,
        [101, 103, 99, 104],
    )

    assert result["Status"] == "STOP_VALIDATED"
    assert result["Entry Price"] == 105
    assert result["Structural Low"] == 99
    assert result["Stop Price"] == 99
    assert result["Stop Distance"] == 6


def test_stop_above_entry_rejected():
    result = evaluate_stop_loss_price(
        build_stop_loss_context(),
        95,
        [96, 98, 100],
    )

    assert result["Status"] == "STOP_REJECTED"


def test_stop_context_not_supported():
    context = build_stop_loss_context()
    context["Stop-Loss Context"] = "STOP_DEVELOPING"

    result = evaluate_stop_loss_price(
        context,
        105,
        [101, 103, 99],
    )

    assert result["Status"] == "STOP_NOT_ESTABLISHED"


def test_insufficient_history():
    result = evaluate_stop_loss_price(
        build_stop_loss_context(),
        105,
        [101, 103],
    )

    assert result["Status"] == "INSUFFICIENT_PRICE_HISTORY"


def test_invalid_entry_price():
    result = evaluate_stop_loss_price(
        build_stop_loss_context(),
        -10,
        [101, 103, 99],
    )

    assert result["Status"] == "REJECTED"


def test_invalid_price_history():
    result = evaluate_stop_loss_price(
        build_stop_loss_context(),
        105,
        [101, "bad", 99],
    )

    assert result["Status"] == "REJECTED"


def test_invalid_input():
    result = evaluate_stop_loss_price(
        None,
        105,
        [101, 103, 99],
    )

    assert result["Status"] == "REJECTED"


def test_missing_field():
    context = build_stop_loss_context()
    del context["Trade Quality"]

    result = evaluate_stop_loss_price(
        context,
        105,
        [101, 103, 99],
    )

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_stop_loss()
    test_stop_above_entry_rejected()
    test_stop_context_not_supported()
    test_insufficient_history()
    test_invalid_entry_price()
    test_invalid_price_history()
    test_invalid_input()
    test_missing_field()

    print("V14.3 Stop-Loss Price: PASS")