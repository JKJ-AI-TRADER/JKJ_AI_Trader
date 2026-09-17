from modules.nifty_option_opportunity_strength import (
    classify_opportunity_strength,
    evaluate_opportunity_strength,
)


def build_classification(classification, confirmation):
    return {
        "Status": "CLASSIFIED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "Momentum Confirmation": confirmation,
        "Market Context": "MOVING_TOGETHER",
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Context": "SUPPORTED",
        "Opportunity Classification": classification,
    }


def test_strong():
    result = evaluate_opportunity_strength(
        build_classification(
            "SUPPORTED_OPPORTUNITY",
            "CONFIRMED",
        )
    )

    assert result["Status"] == "EVALUATED"
    assert result["Opportunity Strength"] == "STRONG"


def test_developing():
    result = evaluate_opportunity_strength(
        build_classification(
            "SUPPORTED_OPPORTUNITY",
            "PARTIALLY_CONFIRMED",
        )
    )

    assert result["Status"] == "EVALUATED"
    assert result["Opportunity Strength"] == "DEVELOPING"


def test_context_conflict():
    result = evaluate_opportunity_strength(
        build_classification(
            "CONTEXT_CONFLICT",
            "CONFIRMED",
        )
    )

    assert result["Status"] == "EVALUATED"
    assert result["Opportunity Strength"] == "WEAK"


def test_no_clear_opportunity():
    result = evaluate_opportunity_strength(
        build_classification(
            "NO_CLEAR_OPPORTUNITY",
            "NOT_CONFIRMED",
        )
    )

    assert result["Status"] == "EVALUATED"
    assert result["Opportunity Strength"] == "WEAK"


def test_mixed_opportunity():
    result = evaluate_opportunity_strength(
        build_classification(
            "MIXED_OPPORTUNITY",
            "PARTIALLY_CONFIRMED",
        )
    )

    assert result["Status"] == "EVALUATED"
    assert result["Opportunity Strength"] == "DEVELOPING"


def test_invalid_input():
    result = evaluate_opportunity_strength(None)

    assert result["Status"] == "REJECTED"


def test_invalid_classification():
    result = classify_opportunity_strength(
        "INVALID_CLASSIFICATION",
        "CONFIRMED",
    )

    assert result == "INVALID"


if __name__ == "__main__":
    test_strong()
    test_developing()
    test_context_conflict()
    test_no_clear_opportunity()
    test_mixed_opportunity()
    test_invalid_input()
    test_invalid_classification()

    print("V12.8 Stage 3 Opportunity Strength: PASS")