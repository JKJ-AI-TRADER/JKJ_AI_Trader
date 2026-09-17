from modules.nifty_option_entry_risk_context import (
    evaluate_entry_risk_context,
)


def build_controlled_context():
    return {
        "Status": "QUALIFIED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",

        "Option Direction": "UP",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Risk Classification": "LOWER_RISK_CONTEXT",
        "Trade Quality": "HIGH_QUALITY_CONTEXT",
    }


def build_developing_context():
    context = build_controlled_context()

    context["Entry Qualification"] = "ENTRY_DEVELOPING"
    context["Risk Classification"] = "MODERATE_RISK_CONTEXT"
    context["Trade Quality"] = "DEVELOPING_QUALITY_CONTEXT"

    return context


def test_controlled_risk():
    result = evaluate_entry_risk_context(
        build_controlled_context()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Entry Risk Context"] == (
        "CONTROLLED_RISK_CONTEXT"
    )


def test_developing_risk():
    result = evaluate_entry_risk_context(
        build_developing_context()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Entry Risk Context"] == (
        "DEVELOPING_RISK_CONTEXT"
    )


def test_elevated_risk():
    context = build_controlled_context()
    context["Entry Qualification"] = "ENTRY_NOT_QUALIFIED"
    context["Risk Classification"] = "HIGHER_RISK_CONTEXT"
    context["Trade Quality"] = "LOW_QUALITY_CONTEXT"

    result = evaluate_entry_risk_context(context)

    assert result["Status"] == "EVALUATED"
    assert result["Entry Risk Context"] == (
        "ELEVATED_RISK_CONTEXT"
    )


def test_undefined_risk():
    context = build_controlled_context()
    context["Entry Qualification"] = "ENTRY_QUALIFIED"
    context["Risk Classification"] = "MODERATE_RISK_CONTEXT"
    context["Trade Quality"] = "DEVELOPING_QUALITY_CONTEXT"

    result = evaluate_entry_risk_context(context)

    assert result["Status"] == "EVALUATED"
    assert result["Entry Risk Context"] == (
        "UNDEFINED_RISK_CONTEXT"
    )


def test_invalid_input():
    result = evaluate_entry_risk_context(None)

    assert result["Status"] == "REJECTED"


def test_invalid_entry_qualification():
    result = evaluate_entry_risk_context({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_missing_field():
    context = build_controlled_context()
    del context["Trade Quality"]

    result = evaluate_entry_risk_context(context)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_controlled_risk()
    test_developing_risk()
    test_elevated_risk()
    test_undefined_risk()
    test_invalid_input()
    test_invalid_entry_qualification()
    test_missing_field()

    print("V14.1 Entry Risk Context: PASS")