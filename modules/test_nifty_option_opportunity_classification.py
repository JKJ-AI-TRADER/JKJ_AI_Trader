from modules.nifty_option_opportunity_classification import (
    classify_opportunity,
    evaluate_opportunity_classification,
)


def build_evidence(momentum_context, momentum_confirmation):
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "Momentum Confirmation": momentum_confirmation,
        "Market Context": "MOVING_TOGETHER",
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Context": momentum_context,
    }


def test_supported_opportunity():
    result = evaluate_opportunity_classification(
        build_evidence("SUPPORTED", "CONFIRMED")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Opportunity Classification"] == "SUPPORTED_OPPORTUNITY"


def test_context_conflict():
    result = evaluate_opportunity_classification(
        build_evidence("CONTEXT_CONFLICT", "CONFIRMED")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Opportunity Classification"] == "CONTEXT_CONFLICT"


def test_mixed_opportunity():
    result = evaluate_opportunity_classification(
        build_evidence("MIXED_CONTEXT", "PARTIALLY_CONFIRMED")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Opportunity Classification"] == "MIXED_OPPORTUNITY"


def test_no_clear_opportunity():
    result = evaluate_opportunity_classification(
        build_evidence("MIXED_CONTEXT", "NOT_CONFIRMED")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Opportunity Classification"] == "MIXED_OPPORTUNITY"


def test_invalid_input():
    result = evaluate_opportunity_classification(None)

    assert result["Status"] == "REJECTED"


def test_invalid_classification():
    result = classify_opportunity(
        "INVALID_CONTEXT",
        "CONFIRMED",
    )

    assert result == "INVALID"


if __name__ == "__main__":
    test_supported_opportunity()
    test_context_conflict()
    test_mixed_opportunity()
    test_no_clear_opportunity()
    test_invalid_input()
    test_invalid_classification()

    print("V12.8 Stage 2 Opportunity Classification: PASS")