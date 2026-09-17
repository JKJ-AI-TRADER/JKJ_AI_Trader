from modules.nifty_option_stop_loss_context import (
    evaluate_stop_loss_context,
)


def build_controlled_context():
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
    }


def test_stop_supported():
    result = evaluate_stop_loss_context(
        build_controlled_context()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Stop-Loss Context"] == "STOP_SUPPORTED"


def test_stop_developing():
    context = build_controlled_context()
    context["Entry Qualification"] = "ENTRY_DEVELOPING"
    context["Risk Classification"] = "MODERATE_RISK_CONTEXT"
    context["Trade Quality"] = "DEVELOPING_QUALITY_CONTEXT"
    context["Entry Risk Context"] = "DEVELOPING_RISK_CONTEXT"

    result = evaluate_stop_loss_context(context)

    assert result["Status"] == "EVALUATED"
    assert result["Stop-Loss Context"] == "STOP_DEVELOPING"


def test_stop_not_supported():
    context = build_controlled_context()
    context["Entry Qualification"] = "ENTRY_NOT_QUALIFIED"
    context["Risk Classification"] = "HIGHER_RISK_CONTEXT"
    context["Trade Quality"] = "LOW_QUALITY_CONTEXT"
    context["Entry Risk Context"] = "ELEVATED_RISK_CONTEXT"

    result = evaluate_stop_loss_context(context)

    assert result["Status"] == "EVALUATED"
    assert result["Stop-Loss Context"] == "STOP_NOT_SUPPORTED"


def test_stop_undefined():
    context = build_controlled_context()
    context["Entry Risk Context"] = "UNDEFINED_RISK_CONTEXT"

    result = evaluate_stop_loss_context(context)

    assert result["Status"] == "EVALUATED"
    assert result["Stop-Loss Context"] == "STOP_UNDEFINED"


def test_invalid_input():
    result = evaluate_stop_loss_context(None)

    assert result["Status"] == "REJECTED"


def test_invalid_entry_risk_context():
    result = evaluate_stop_loss_context({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_missing_field():
    context = build_controlled_context()
    del context["Trade Quality"]

    result = evaluate_stop_loss_context(context)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_stop_supported()
    test_stop_developing()
    test_stop_not_supported()
    test_stop_undefined()
    test_invalid_input()
    test_invalid_entry_risk_context()
    test_missing_field()

    print("V14.2 Stop-Loss Context: PASS")
    