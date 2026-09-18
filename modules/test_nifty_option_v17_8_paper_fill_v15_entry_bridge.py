from nifty_option_v17_8_paper_fill_v15_entry_bridge import (
    map_paper_fill_to_v15_entry,
)


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
            "Contract Valid": True,
            "Execution Ready": True,
            "Paper Fill Status": "FILLED",
            "Fill Type": "FULL",
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
        },
    }


def valid_v15_qualification():
    return {
        "Status": "QUALIFIED",
        "Paper Trade Permission": "PERMITTED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Entry Price": 300.0,
        "Stop Price": 270.0,
        "Target 1": 330.0,
        "Target 2": 360.0,
        "Target 3": 390.0,
        "Risk Reward 1": 1.0,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,
        "Entry Qualification": "QUALIFIED",
        "Qualification Reason": "V14.5 exit-qualified setup",
    }


def test_valid_mapping():
    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_COMPLETE"

    mapping = result["V15 Entry Mapping"]

    assert mapping["Status"] == "MAPPED"
    assert mapping["Trade ID"] == "JKJ-TRADE-001"
    assert mapping["Trading Symbol"] == "NIFTY2692223300CE"
    assert mapping["Instrument Type"] == "OPTION"
    assert mapping["Underlying"] == "NIFTY"
    assert mapping["Quantity"] == 65
    assert mapping["Entry Price"] == 305.0


def test_fill_price_becomes_execution_entry_price():
    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Entry Price"] == 305.0
    assert mapping["Qualified Entry Price"] == 300.0


def test_v15_risk_fields_are_preserved():
    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    mapping = result["V15 Entry Mapping"]

    assert mapping["Stop Loss"] == 270.0
    assert mapping["Target 1"] == 330.0
    assert mapping["Target 2"] == 360.0
    assert mapping["Target 3"] == 390.0
    assert mapping["Risk Reward 1"] == 1.0
    assert mapping["Risk Reward 2"] == 2.0
    assert mapping["Risk Reward 3"] == 3.0


def test_symbol_mismatch_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Trading Symbol"] = "NIFTY2692223300PE"

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_unqualified_v15_blocked():
    qualification = valid_v15_qualification()
    qualification["Status"] = "REJECTED"

    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        qualification,
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_v15_permission_blocked():
    qualification = valid_v15_qualification()
    qualification["Paper Trade Permission"] = "NOT_PERMITTED"

    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        qualification,
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_partial_fill_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Fill Type"] = "PARTIAL"
    fill["Paper Fill"]["Filled Quantity"] = 20

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_sell_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Transaction Type"] = "SELL"

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_invalid_contract_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Contract Valid"] = False

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_invalid_quantity_blocked():
    fill = valid_paper_fill()
    fill["Paper Fill"]["Filled Quantity"] = 75

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_missing_trade_id_blocked():
    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        valid_v15_qualification(),
        "",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_broker_communication_blocked():
    fill = valid_paper_fill()
    fill["Broker Communication"] = True

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_live_order_blocked():
    fill = valid_paper_fill()
    fill["Order Placement Permitted"] = True

    result = map_paper_fill_to_v15_entry(
        fill,
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Status"] == "V15_ENTRY_MAPPING_BLOCKED"


def test_mapping_does_not_enable_live_execution():
    result = map_paper_fill_to_v15_entry(
        valid_paper_fill(),
        valid_v15_qualification(),
        "JKJ-TRADE-001",
    )

    assert result["Paper Execution"] is True
    assert result["Broker Communication"] is False
    assert result["Order Placement Permitted"] is False
    assert result["Capital Reassignment"] is False
    assert result["Automatic Ranking"] is False


print("ALL V17.8.5 TESTS PASSED")
