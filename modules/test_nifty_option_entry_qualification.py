from modules.nifty_option_entry_qualification import (
    evaluate_entry_qualification,
)


def build_qualified_context():
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",

        "Option Direction": "UP",
        "Momentum Confirmation": "CONFIRMED",
        "Market Context": "MOVING_TOGETHER",
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Context": "SUPPORTED",

        "Opportunity Classification": "SUPPORTED_OPPORTUNITY",
        "Opportunity Strength": "STRONG",

        "Risk Classification": "LOWER_RISK_CONTEXT",
        "Trade Quality": "HIGH_QUALITY_CONTEXT",
    }


def build_developing_context():
    context = build_qualified_context()

    context["Momentum Confirmation"] = "PARTIALLY_CONFIRMED"
    context["Opportunity Strength"] = "DEVELOPING"
    context["Risk Classification"] = "MODERATE_RISK_CONTEXT"
    context["Trade Quality"] = "DEVELOPING_QUALITY_CONTEXT"

    return context


def test_entry_qualified():
    result = evaluate_entry_qualification(
        build_qualified_context()
    )

    assert result["Status"] == "QUALIFIED"
    assert result["Entry Qualification"] == "ENTRY_QUALIFIED"


def test_entry_developing():
    result = evaluate_entry_qualification(
        build_developing_context()
    )

    assert result["Status"] == "QUALIFIED"
    assert result["Entry Qualification"] == "ENTRY_DEVELOPING"


def test_entry_not_qualified():
    context = build_qualified_context()
    context["Risk Classification"] = "HIGHER_RISK_CONTEXT"

    result = evaluate_entry_qualification(context)

    assert result["Status"] == "QUALIFIED"
    assert result["Entry Qualification"] == (
        "ENTRY_NOT_QUALIFIED"
    )


def test_invalid_input():
    result = evaluate_entry_qualification(None)

    assert result["Status"] == "REJECTED"


def test_invalid_decision_context():
    result = evaluate_entry_qualification({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_missing_field():
    context = build_qualified_context()
    del context["Trade Quality"]

    result = evaluate_entry_qualification(context)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_entry_qualified()
    test_entry_developing()
    test_entry_not_qualified()
    test_invalid_input()
    test_invalid_decision_context()
    test_missing_field()

    print("V13.2 Entry Qualification: PASS")