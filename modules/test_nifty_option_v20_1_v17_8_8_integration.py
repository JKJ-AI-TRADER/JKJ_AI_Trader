"""
JKJ AI Trader
V20.1 -> V17.8.8 Integration Test
"""

from nifty_option_v20_1_v17_8_8_integration import (
    integrate_v20_1_to_v17_8_8,
)


SYMBOL = "NIFTY26SEP25000CE"


def valid_v20_1_v17_8_7_result():
    trade = {
        "Trade ID": "JKJ-TRADE-001",
        "Status": "OPEN",
        "Symbol": SYMBOL,
        "Instrument Type": "OPTION",
        "Entry Price": 100.0,
        "Original Quantity": 195,
        "Current Quantity": 195,
        "Stop Loss": 90.0,
        "Target": 120.0,
    }

    qualification = {
        "Status": "QUALIFIED",
        "Trading Symbol": SYMBOL,
        "Paper Trade Permission": "PERMITTED",
    }

    v17_8_7_result = {
        "Status": "V17_8_7_PAPER_HANDOFF_COMPLETE",
        "Trade": trade,
        "Paper Trade Qualification": qualification,
        "V15 Handoff": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

    return {
        "Status": "V20_1_V17_8_7_INTEGRATION_COMPLETE",
        "V17.8.7 Result": v17_8_7_result,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def test_successful_lifecycle_boundary():
    result = integrate_v20_1_to_v17_8_8(
        valid_v20_1_v17_8_7_result()
    )

    assert (
        result["Status"]
        == "V20_1_V17_8_8_INTEGRATION_COMPLETE"
    )

    assert result["Lifecycle Ready"] is True
    assert result["Lifecycle Owner"] == "V15.4 / V11"
    assert result["Trade ID"] == "JKJ-TRADE-001"
    assert result["Symbol"] == SYMBOL
    assert result["Current Quantity"] == 195

    print(
        "Successful V20.1 -> V17.8.8 lifecycle boundary: PASS"
    )


def test_incomplete_v17_8_7_blocked():
    result = valid_v20_1_v17_8_7_result()

    result["V17.8.7 Result"]["Status"] = (
        "V17_8_7_PAPER_HANDOFF_REJECTED"
    )

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )
    assert output["Lifecycle Ready"] is False

    print(
        "Incomplete V17.8.7 safeguard: PASS"
    )


def test_broker_communication_blocked():
    result = valid_v20_1_v17_8_7_result()
    result["Broker Communication"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "Broker communication safeguard: PASS"
    )


def test_live_order_blocked():
    result = valid_v20_1_v17_8_7_result()
    result["Order Placement Permitted"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "Live order placement safeguard: PASS"
    )


def test_capital_reassignment_blocked():
    result = valid_v20_1_v17_8_7_result()
    result["Capital Reassignment"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "Capital reassignment safeguard: PASS"
    )


def test_automatic_ranking_blocked():
    result = valid_v20_1_v17_8_7_result()
    result["Automatic Ranking"] = True

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "Automatic ranking safeguard: PASS"
    )


def test_trade_not_open_blocked():
    result = valid_v20_1_v17_8_7_result()

    result["V17.8.7 Result"]["Trade"]["Status"] = "CLOSED"

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "Non-OPEN V11 trade safeguard: PASS"
    )


def test_v15_permission_blocked():
    result = valid_v20_1_v17_8_7_result()

    result["V17.8.7 Result"][
        "Paper Trade Qualification"
    ]["Paper Trade Permission"] = "NOT_PERMITTED"

    output = integrate_v20_1_to_v17_8_8(result)

    assert (
        output["Status"]
        == "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    print(
        "V15 paper permission safeguard: PASS"
    )


def run_test():
    test_successful_lifecycle_boundary()
    test_incomplete_v17_8_7_blocked()
    test_broker_communication_blocked()
    test_live_order_blocked()
    test_capital_reassignment_blocked()
    test_automatic_ranking_blocked()
    test_trade_not_open_blocked()
    test_v15_permission_blocked()

    print()
    print(
        "V20.1 -> V17.8.8 INTEGRATION: ALL TESTS PASSED"
    )
    print("V15.4 / V11 remains lifecycle authority.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No lifecycle action performed.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()