from intraday_paper_trading import open_paper_trade
from intraday_option_paper_session import run_option_paper_session


def test_1_healthy_session_remains_open():

    trade = open_paper_trade(
        trade_id="TEST-V11-001",
        symbol="NIFTY26SEP23300CE",
        instrument_type="OPTION",
        entry_price=100.0,
        quantity=75,
        stop_loss=95.0,
        target=110.0,
        momentum_score=88,
        entry_status="STRONG ENTRY CANDIDATE",
        entry_reason="V11 test",
        expiry="2026-09-15",
        strike=23300,
        option_type="CE",
        underlying="NIFTY",
    )

    result = run_option_paper_session(
        trade,
        [100.0, 101.0, 102.0],
    )

    assert result["Status"] == "READY"
    assert result["Session Status"] == "OPEN"
    assert result["Final Quantity"] == 75
    assert result["Peak Price"] == 102.0

    print("TEST 1 PASSED")


def test_2_target_exit_closes_trade():

    trade = open_paper_trade(
        trade_id="TEST-V11-002",
        symbol="NIFTY26SEP23300CE",
        instrument_type="OPTION",
        entry_price=100.0,
        quantity=75,
        stop_loss=95.0,
        target=105.0,
        momentum_score=88,
        entry_status="STRONG ENTRY CANDIDATE",
        entry_reason="V11 test",
        expiry="2026-09-15",
        strike=23300,
        option_type="CE",
        underlying="NIFTY",
    )

    result = run_option_paper_session(
        trade,
        [100.0, 102.0, 105.0],
    )

    assert result["Status"] == "READY"
    assert result["Session Status"] == "CLOSED"
    assert result["Final Quantity"] == 0
    assert result["Gross P&L"] > 0
    assert result["Exit Reason"] is not None

    print("TEST 2 PASSED")


def test_3_stop_loss_exit_closes_trade():

    trade = open_paper_trade(
        trade_id="TEST-V11-003",
        symbol="NIFTY26SEP23300CE",
        instrument_type="OPTION",
        entry_price=100.0,
        quantity=75,
        stop_loss=95.0,
        target=110.0,
        momentum_score=88,
        entry_status="STRONG ENTRY CANDIDATE",
        entry_reason="V11 test",
        expiry="2026-09-15",
        strike=23300,
        option_type="CE",
        underlying="NIFTY",
    )

    result = run_option_paper_session(
        trade,
        [100.0, 98.0, 94.0],
    )

    assert result["Status"] == "READY"
    assert result["Session Status"] == "CLOSED"
    assert result["Final Quantity"] == 0
    assert result["Exit Reason"] == "STOP LOSS"

    print("TEST 3 PASSED")


def test_4_empty_price_sequence_rejected():

    trade = open_paper_trade(
        trade_id="TEST-V11-004",
        symbol="NIFTY26SEP23300CE",
        instrument_type="OPTION",
        entry_price=100.0,
        quantity=75,
        stop_loss=95.0,
        target=110.0,
        momentum_score=88,
        entry_status="STRONG ENTRY CANDIDATE",
        entry_reason="V11 test",
        expiry="2026-09-15",
        strike=23300,
        option_type="CE",
        underlying="NIFTY",
    )

    result = run_option_paper_session(
        trade,
        [],
    )

    assert result["Status"] == "INVALID"
    assert result["Session Status"] == "NOT STARTED"

    print("TEST 4 PASSED")


def test_5_invalid_trade_rejected():

    result = run_option_paper_session(
        "INVALID TRADE",
        [100.0, 101.0],
    )

    assert result["Status"] == "INVALID"
    assert result["Session Status"] == "NOT STARTED"

    print("TEST 5 PASSED")
def test_6_partial_exit_and_continuation():

    trade = open_paper_trade(
        trade_id="TEST-V11-006",
        symbol="NIFTY26SEP23300CE",
        instrument_type="OPTION",
        entry_price=100.0,
        quantity=75,
        stop_loss=95.0,
        target=130.0,
        momentum_score=88,
        entry_status="STRONG ENTRY CANDIDATE",
        entry_reason="V11 partial exit test",
        expiry="2026-09-15",
        strike=23300,
        option_type="CE",
        underlying="NIFTY",
    )

    result = run_option_paper_session(
        trade,
        [
            100.0,
            104.0,
            110.0,
            108.0,
            107.0,
            106.0,
        ],
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
    )

    assert result["Status"] == "READY"

    assert len(result["Session Events"]) > 0

    partial_exit_found = any(
        event.get("Exit Result", {})
        .get("Slicing Result", {})
        .get("Slice Decision") == "PARTIAL EXIT"
        for event in result["Session Events"]
    )

    assert partial_exit_found

    assert result["Final Quantity"] == 24

    assert result["Gross P&L"] > 0

    print("TEST 6 PASSED")

def test_7_partial_exits_then_final_target_exit():

        trade = open_paper_trade(
            trade_id="TEST-V11-007",
            symbol="NIFTY26SEP23300CE",
            instrument_type="OPTION",
            entry_price=100.0,
            quantity=75,
            stop_loss=95.0,
            target=120.0,
            momentum_score=88,
            entry_status="STRONG ENTRY CANDIDATE",
            entry_reason="V11 full lifecycle test",
            expiry="2026-09-15",
            strike=23300,
            option_type="CE",
            underlying="NIFTY",
        )

        result = run_option_paper_session(
            trade,
            [
                100.0,
                110.0,
                108.0,
                106.0,
                120.0,
            ],
            momentum_status="WEAK",
            volume_status="DECREASING",
            underlying_status="SUPPORTIVE",
            structure_status="STRONG",
        )

        assert result["Status"] == "READY"

        assert result["Session Status"] == "OPEN"

        assert result["Final Quantity"] == 0

        assert result["Gross P&L"] > 0

        partial_exit_count = sum(
            1
            for event in result["Session Events"]
            if event.get("Exit Result", {})
            .get("Slicing Result", {})
            .get("Slice Decision") == "PARTIAL EXIT"
        )

        assert partial_exit_count >= 1

        assert result["Exit Reason"] == "TARGET REACHED"

        print("TEST 7 PASSED")

def test_7_partial_exits_then_final_target_exit():

        trade = open_paper_trade(
            trade_id="TEST-V11-007",
            symbol="NIFTY26SEP23300CE",
            instrument_type="OPTION",
            entry_price=100.0,
            quantity=75,
            stop_loss=95.0,
            target=120.0,
            momentum_score=88,
            entry_status="STRONG ENTRY CANDIDATE",
            entry_reason="V11 full lifecycle test",
            expiry="2026-09-15",
            strike=23300,
            option_type="CE",
            underlying="NIFTY",
    )

        result = run_option_paper_session(
        trade,
        [
            100.0,
            110.0,
            108.0,
            106.0,
            120.0,
        ],
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
    )

        assert result["Status"] == "READY"

        assert result["Session Status"] == "CLOSED"

        assert result["Final Quantity"] == 0

        assert result["Gross P&L"] > 0

        partial_exit_count = sum(
            1
            for event in result["Session Events"]
            if event.get("Exit Result", {})
            .get("Slicing Result", {})
            .get("Slice Decision") == "PARTIAL EXIT"
    )

        assert partial_exit_count >= 1

        assert result["Exit Reason"] == "TARGET REACHED"

        print("TEST 7 PASSED")    

if __name__ == "__main__":
    

        test_1_healthy_session_remains_open()
        test_2_target_exit_closes_trade()
        test_3_stop_loss_exit_closes_trade()
        test_4_empty_price_sequence_rejected()
        test_5_invalid_trade_rejected()
        test_6_partial_exit_and_continuation()
        test_7_partial_exits_then_final_target_exit()

        print()
        print("ALL V11 TESTS PASSED")