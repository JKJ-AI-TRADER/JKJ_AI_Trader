"""
JKJ AI Trader
Test — NIFTY Option Momentum Context — V12.7 Stage 3
"""

from modules.nifty_option_momentum_context import (
    classify_momentum_context,
    evaluate_momentum_context,
)


def build_momentum(state):

    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTYTESTCE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "Momentum Confirmation": state,
    }


def build_context(context):

    return {
        "Status": "CLASSIFIED",
        "Trading Symbol": "NIFTYTESTCE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "NIFTY Movement Evidence": True,
        "Movement Relationship": context,
        "Market Context": context,
    }


def test_confirmed_supported():

    assert (
        classify_momentum_context(
            "CONFIRMED",
            "MOVING_TOGETHER",
        )
        == "SUPPORTED"
    )


def test_confirmed_option_moving_nifty_flat():

    assert (
        classify_momentum_context(
            "CONFIRMED",
            "OPTION_MOVING_NIFTY_FLAT",
        )
        == "SUPPORTED"
    )


def test_confirmed_diverging():

    assert (
        classify_momentum_context(
            "CONFIRMED",
            "DIVERGING",
        )
        == "CONTEXT_CONFLICT"
    )


def test_confirmed_nifty_moving_option_flat():

    assert (
        classify_momentum_context(
            "CONFIRMED",
            "OPTION_FLAT_NIFTY_MOVING",
        )
        == "CONTEXT_CONFLICT"
    )


def test_confirmed_both_flat():

    assert (
        classify_momentum_context(
            "CONFIRMED",
            "BOTH_FLAT",
        )
        == "CONTEXT_CONFLICT"
    )


def test_partial_confirmation():

    assert (
        classify_momentum_context(
            "PARTIALLY_CONFIRMED",
            "MOVING_TOGETHER",
        )
        == "MIXED_CONTEXT"
    )


def test_not_confirmed():

    assert (
        classify_momentum_context(
            "NOT_CONFIRMED",
            "MOVING_TOGETHER",
        )
        == "MIXED_CONTEXT"
    )


def test_invalid_state():

    assert (
        classify_momentum_context(
            "UNKNOWN",
            "MOVING_TOGETHER",
        )
        == "INVALID"
    )


def test_valid_combination():

    result = evaluate_momentum_context(
        build_momentum("CONFIRMED"),
        build_context("MOVING_TOGETHER"),
    )

    assert result["Status"] == "EVALUATED"
    assert result["Momentum Context"] == "SUPPORTED"


def test_conflicting_combination():

    result = evaluate_momentum_context(
        build_momentum("CONFIRMED"),
        build_context("DIVERGING"),
    )

    assert result["Status"] == "EVALUATED"
    assert result["Momentum Context"] == "CONTEXT_CONFLICT"


def test_partial_combination():

    result = evaluate_momentum_context(
        build_momentum("PARTIALLY_CONFIRMED"),
        build_context("MOVING_TOGETHER"),
    )

    assert result["Status"] == "EVALUATED"
    assert result["Momentum Context"] == "MIXED_CONTEXT"


def test_invalid_momentum_status():

    momentum = build_momentum("CONFIRMED")
    momentum["Status"] = "INVALID"

    result = evaluate_momentum_context(
        momentum,
        build_context("MOVING_TOGETHER"),
    )

    assert result["Status"] == "REJECTED"


def test_invalid_context_status():

    context = build_context("MOVING_TOGETHER")
    context["Status"] = "INVALID"

    result = evaluate_momentum_context(
        build_momentum("CONFIRMED"),
        context,
    )

    assert result["Status"] == "REJECTED"


def test_missing_momentum_field():

    momentum = build_momentum("CONFIRMED")
    del momentum["Momentum Confirmation"]

    result = evaluate_momentum_context(
        momentum,
        build_context("MOVING_TOGETHER"),
    )

    assert result["Status"] == "REJECTED"


def test_missing_context_field():

    context = build_context("MOVING_TOGETHER")
    del context["Movement Relationship"]

    result = evaluate_momentum_context(
        build_momentum("CONFIRMED"),
        context,
    )

    assert result["Status"] == "REJECTED"


def test_invalid_input():

    result = evaluate_momentum_context(
        None,
        None,
    )

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_confirmed_supported()
    test_confirmed_option_moving_nifty_flat()
    test_confirmed_diverging()
    test_confirmed_nifty_moving_option_flat()
    test_confirmed_both_flat()
    test_partial_confirmation()
    test_not_confirmed()
    test_invalid_state()
    test_valid_combination()
    test_conflicting_combination()
    test_partial_combination()
    test_invalid_momentum_status()
    test_invalid_context_status()
    test_missing_momentum_field()
    test_missing_context_field()
    test_invalid_input()

    print(
        "V12.7 Stage 3 Momentum Context: PASS"
    )