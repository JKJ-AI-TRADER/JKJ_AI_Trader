from nifty_option_v17_8_paper_fill_engine import simulate_paper_fill


def valid_paper_order():
    return {
        "Status": "PAPER_ORDER_ACCEPTED",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Paper Order": {
            "Paper Order ID": "JKJ-PAPER-ORDER-001",
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
            "Paper Status": "PAPER_ACCEPTED",
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
        },
    }


def test_full_fill_at_reference_price():
    result = simulate_paper_fill(valid_paper_order())

    assert result["Status"] == "PAPER_FILL_COMPLETE"

    fill = result["Paper Fill"]

    assert fill["Paper Fill Status"] == "FILLED"
    assert fill["Fill Type"] == "FULL"
    assert fill["Requested Quantity"] == 65
    assert fill["Filled Quantity"] == 65
    assert fill["Fill Price"] == 300.0


def test_full_fill_at_supplied_price():
    result = simulate_paper_fill(
        valid_paper_order(),
        fill_price=305.0,
    )

    fill = result["Paper Fill"]

    assert result["Status"] == "PAPER_FILL_COMPLETE"
    assert fill["Fill Price"] == 305.0
    assert fill["Simulated Fill Capital"] == 305.0 * 65


def test_unaccepted_order_blocked():
    order = valid_paper_order()
    order["Status"] = "PAPER_ORDER_BLOCKED"

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_broker_communication_blocked():
    order = valid_paper_order()
    order["Broker Communication"] = True

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_live_order_placement_blocked():
    order = valid_paper_order()
    order["Order Placement Permitted"] = True

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_capital_reassignment_blocked():
    order = valid_paper_order()
    order["Capital Reassignment"] = True

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_automatic_ranking_blocked():
    order = valid_paper_order()
    order["Automatic Ranking"] = True

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_sell_order_blocked():
    order = valid_paper_order()
    order["Paper Order"]["Transaction Type"] = "SELL"

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_invalid_quantity_blocked():
    order = valid_paper_order()
    order["Paper Order"]["Quantity"] = 75

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_invalid_contract_blocked():
    order = valid_paper_order()
    order["Paper Order"]["Contract Valid"] = False

    result = simulate_paper_fill(order)

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_invalid_fill_price_blocked():
    result = simulate_paper_fill(
        valid_paper_order(),
        fill_price=0,
    )

    assert result["Status"] == "PAPER_FILL_BLOCKED"


def test_fill_quantity_equals_requested_quantity():
    result = simulate_paper_fill(valid_paper_order())

    fill = result["Paper Fill"]

    assert fill["Filled Quantity"] == fill["Requested Quantity"]


def test_safety_flags_remain_disabled():
    result = simulate_paper_fill(valid_paper_order())

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False


print("ALL V17.8.2 TESTS PASSED")
