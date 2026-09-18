from nifty_option_v17_8_paper_position import create_paper_position


def valid_paper_fill():
    return {
        "Status": "PAPER_FILL_COMPLETE",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Paper Fill": {
            "Paper Fill ID": "JKJ-PAPER-ORDER-001-FILL-001",
            "Paper Order ID": "JKJ-PAPER-ORDER-001",
            "Candidate": "NIFTY 23300 CE",
            "Priority": 1,
            "Priority Source": "DECISION_RISK_LAYER",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Transaction Type": "BUY",
            "Order Type": "MARKET",
            "Product": "MIS",
            "Requested Quantity": 65,
            "Filled Quantity": 65,
            "Lot Size": 65,
            "Entry Price Reference": 300.0,
            "Fill Price": 305.0,
            "Required Capital at Request": 19500.0,
            "Simulated Fill Capital": 19825.0,
            "Contract Valid": True,
            "Execution Ready": True,
            "Paper Order Status": "PAPER_ACCEPTED",
            "Paper Fill Status": "FILLED",
            "Fill Type": "FULL",
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
        },
    }


def test_valid_position_creation():
    result = create_paper_position(valid_paper_fill())

    assert result["Status"] == "PAPER_POSITION_CREATED"

    position = result["Paper Position"]

    assert position["Paper Status"] == "PAPER_POSITION_OPEN"
    assert position["Position Type"] == "LONG"
    assert position["Transaction Type"] == "BUY"
    assert position["Trading Symbol"] == "NIFTY2692223300CE"
    assert position["Quantity"] == 65
    assert position["Entry Price"] == 305.0
    assert position["Capital Used"] == 19825.0


def test_position_quantity_equals_filled_quantity():
    result = create_paper_position(valid_paper_fill())

    position = result["Paper Position"]

    assert position["Quantity"] == 65


def test_position_capital_matches_fill():
    result = create_paper_position(valid_paper_fill())

    position = result["Paper Position"]

    assert position["Capital Used"] == position["Entry Price"] * position["Quantity"]


def test_incomplete_fill_blocked():
    fill = valid_paper_fill()
    fill["Status"] = "PAPER_FILL_BLOCKED"

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_partial_fill_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Fill Type"] = "PARTIAL"
    fill["Paper Fill"]["Filled Quantity"] = 20

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_quantity_mismatch_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Filled Quantity"] = 20

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_invalid_lot_quantity_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Filled Quantity"] = 75
    fill["Paper Fill"]["Requested Quantity"] = 75

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_invalid_contract_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Contract Valid"] = False

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_sell_fill_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Transaction Type"] = "SELL"

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_capital_calculation_mismatch_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Simulated Fill Capital"] = 20000.0

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_broker_communication_blocked():
    fill = valid_paper_fill()
    fill["Broker Communication"] = True

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_live_order_placement_blocked():
    fill = valid_paper_fill()
    fill["Order Placement Permitted"] = True

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_capital_reassignment_blocked():
    fill = valid_paper_fill()
    fill["Capital Reassignment"] = True

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_automatic_ranking_blocked():
    fill = valid_paper_fill()
    fill["Automatic Ranking"] = True

    result = create_paper_position(fill)

    assert result["Status"] == "PAPER_POSITION_BLOCKED"


def test_safety_flags_remain_disabled():
    result = create_paper_position(valid_paper_fill())

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False


print("ALL V17.8.3 TESTS PASSED")
