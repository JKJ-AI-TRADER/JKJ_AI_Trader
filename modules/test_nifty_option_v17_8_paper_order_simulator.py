from nifty_option_v17_8_paper_order_simulator import simulate_paper_order


def valid_execution_request():
    return {
        "Status": "EXECUTION_REQUEST_SPECIFIED",
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Execution Request": {
            "Candidate": "NIFTY 23300 CE",
            "Priority": 1,
            "Priority Source": "DECISION_RISK_LAYER",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Transaction Type": "BUY",
            "Order Type": "MARKET",
            "Product": "MIS",
            "Quantity": 65,
            "Lot Size": 65,
            "Entry Price Reference": 300.0,
            "Allocated Capital": 20000.0,
            "Required Capital": 19500.0,
            "Contract Valid": True,
            "Execution Ready": True,
            "Order Placement Permitted": False,
            "Broker Communication": False,
        },
    }


def test_valid_market_order():
    result = simulate_paper_order(valid_execution_request())

    assert result["Status"] == "PAPER_ORDER_ACCEPTED"

    order = result["Paper Order"]

    assert order["Paper Status"] == "PAPER_ACCEPTED"
    assert order["Quantity"] == 65
    assert order["Trading Symbol"] == "NIFTY2692223300CE"
    assert order["Transaction Type"] == "BUY"
    assert order["Order Type"] == "MARKET"
    assert order["Product"] == "MIS"


def test_valid_limit_order():
    request = valid_execution_request()
    request["Execution Request"]["Order Type"] = "LIMIT"

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_ACCEPTED"
    assert result["Paper Order"]["Order Type"] == "LIMIT"


def test_invalid_status_blocked():
    request = valid_execution_request()
    request["Status"] = "BROKER_REQUEST_PREPARED"

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_broker_communication_blocked():
    request = valid_execution_request()
    request["Broker Communication"] = True

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_live_order_placement_blocked():
    request = valid_execution_request()
    request["Order Placement Permitted"] = True

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_capital_reassignment_blocked():
    request = valid_execution_request()
    request["Capital Reassignment"] = True

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_automatic_ranking_blocked():
    request = valid_execution_request()
    request["Automatic Ranking"] = True

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_sell_blocked():
    request = valid_execution_request()
    request["Execution Request"]["Transaction Type"] = "SELL"

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_invalid_quantity_blocked():
    request = valid_execution_request()
    request["Execution Request"]["Quantity"] = 75

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_invalid_contract_blocked():
    request = valid_execution_request()
    request["Execution Request"]["Contract Valid"] = False

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_capital_exceeded_blocked():
    request = valid_execution_request()
    request["Execution Request"]["Required Capital"] = 21000.0

    result = simulate_paper_order(request)

    assert result["Status"] == "PAPER_ORDER_BLOCKED"


def test_quantity_preserved():
    request = valid_execution_request()

    result = simulate_paper_order(request)

    assert result["Paper Order"]["Quantity"] == 65


def test_safety_flags_remain_disabled():
    result = simulate_paper_order(valid_execution_request())

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False


print("ALL V17.8.1 TESTS PASSED")
