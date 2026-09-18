from nifty_option_v17_8_paper_execution_audit import (
    create_paper_execution_audit,
)


def valid_paper_position():
    return {
        "Status": "PAPER_POSITION_CREATED",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Paper Position": {
            "Paper Position ID": "JKJ-PAPER-ORDER-001-FILL-001-POSITION-001",
            "Paper Fill ID": "JKJ-PAPER-ORDER-001-FILL-001",
            "Paper Order ID": "JKJ-PAPER-ORDER-001",
            "Candidate": "NIFTY 23300 CE",
            "Priority": 1,
            "Priority Source": "DECISION_RISK_LAYER",
            "Trading Symbol": "NIFTY2692223300CE",
            "Instrument Token": 14588162,
            "Position Type": "LONG",
            "Transaction Type": "BUY",
            "Order Type": "MARKET",
            "Product": "MIS",
            "Quantity": 65,
            "Lot Size": 65,
            "Entry Price": 305.0,
            "Entry Price Reference": 300.0,
            "Capital Used": 19825.0,
            "Contract Valid": True,
            "Execution Ready": True,
            "Paper Status": "PAPER_POSITION_OPEN",
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
        },
    }


def test_valid_audit():
    result = create_paper_execution_audit(valid_paper_position())

    assert result["Status"] == "PAPER_EXECUTION_AUDIT_COMPLETE"

    audit = result["Audit Record"]

    assert audit["Audit Status"] == "PAPER_EXECUTION_AUDITED"
    assert audit["Audit Scope"] == "POSITION_CREATION"
    assert audit["Read Only"] is True
    assert audit["Trading Symbol"] == "NIFTY2692223300CE"
    assert audit["Quantity"] == 65
    assert audit["Entry Price"] == 305.0
    assert audit["Capital Used"] == 19825.0


def test_audit_preserves_position_identity():
    result = create_paper_execution_audit(valid_paper_position())

    audit = result["Audit Record"]

    assert audit["Paper Position ID"].endswith("POSITION-001")
    assert audit["Paper Fill ID"] == "JKJ-PAPER-ORDER-001-FILL-001"
    assert audit["Paper Order ID"] == "JKJ-PAPER-ORDER-001"


def test_audit_capital_matches_position():
    result = create_paper_execution_audit(valid_paper_position())

    audit = result["Audit Record"]

    assert audit["Capital Used"] == audit["Entry Price"] * audit["Quantity"]


def test_invalid_position_status_blocked():
    position = valid_paper_position()
    position["Status"] = "PAPER_POSITION_BLOCKED"

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_closed_position_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Paper Status"] = "PAPER_POSITION_CLOSED"

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_non_long_position_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Position Type"] = "SHORT"

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_sell_position_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Transaction Type"] = "SELL"

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_invalid_quantity_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Quantity"] = 75

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_invalid_contract_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Contract Valid"] = False

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_capital_mismatch_blocked():
    position = valid_paper_position()
    position["Paper Position"]["Capital Used"] = 20000.0

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_broker_communication_blocked():
    position = valid_paper_position()
    position["Broker Communication"] = True

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_live_order_placement_blocked():
    position = valid_paper_position()
    position["Order Placement Permitted"] = True

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_capital_reassignment_blocked():
    position = valid_paper_position()
    position["Capital Reassignment"] = True

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_automatic_ranking_blocked():
    position = valid_paper_position()
    position["Automatic Ranking"] = True

    result = create_paper_execution_audit(position)

    assert result["Status"] == "PAPER_AUDIT_BLOCKED"


def test_safety_flags_remain_disabled():
    result = create_paper_execution_audit(valid_paper_position())

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False
    assert result["Read Only"] is True


print("ALL V17.8.4 TESTS PASSED")
