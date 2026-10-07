"""
JKJ AI Trader
V16.2 Stage 4A — Real-Market Paper Position Update

Purpose:
Validate fresh Zerodha market prices against an existing
V15 paper position.

This test does NOT:
- place live orders
- create live positions
- make new entry decisions
- modify V11
- modify V12-V15
- modify main.py
"""

from modules.nifty_option_v16_2_real_market_sequence import (
    collect_real_market_sequence,
)

from modules.nifty_option_v16_real_market_paper_validation import (
    validate_real_market_paper_entry,
)

from modules.nifty_option_paper_position_lifecycle import (
    update_paper_position,
)


def main():

    print("\nJKJ AI Trader — V16.2 Stage 4A")
    print("Real-Market Paper Position Update")
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. Create a fresh real-market qualified paper trade
    # ---------------------------------------------------------

    sequence_result = collect_real_market_sequence(
        option_type="CE",
        observation_count=4,
        interval_seconds=10,
    )

    if sequence_result.get("Status") != "SEQUENCE_RECORDED":
        print("\nStage 4A stopped safely.")
        print("Reason:")
        print(sequence_result.get("Reason"))
        return

    observations = sequence_result.get(
        "Observations",
        [],
    )

    validation_result = validate_real_market_paper_entry(
        observations=observations,
        quantity=75,
        trade_id="V16.2-REAL-TEST-002",
    )

    print("\nPaper Entry Validation:")
    print(validation_result.get("Status"))

    if validation_result.get("Status") != "PAPER_TRADE_OPENED":
        print("\nNo paper position created.")
        print("Stage 4A stopped safely.")
        return

    trade = validation_result["Paper Trade Result"]["Trade"]

    print("\nPaper Position Created:")
    print("Symbol:", trade.get("Symbol"))
    print("Entry Price:", trade.get("Entry Price"))
    print("Quantity:", trade.get("Current Quantity"))
    print("Stop Loss:", trade.get("Stop Loss"))
    print("Target:", trade.get("Target"))

    # ---------------------------------------------------------
    # 2. Collect fresh real-market prices
    # ---------------------------------------------------------

    followup_result = collect_real_market_sequence(
        option_type=trade.get("Option Type"),
        observation_count=3,
        interval_seconds=10,
    )

    if followup_result.get("Status") != "SEQUENCE_RECORDED":
        print("\nFollow-up observation stopped safely.")
        print("Reason:")
        print(followup_result.get("Reason"))
        return

    followup_observations = followup_result.get(
        "Observations",
        [],
    )

    # ---------------------------------------------------------
    # 3. Update paper position with real prices
    # ---------------------------------------------------------

    for observation in followup_observations:

        current_price = observation.get(
            "Current Price"
        )

        update_result = update_paper_position(
            trade=trade,
            current_price=current_price,
        )

        print(
            "\nReal Price:",
            current_price,
            "| Update:",
            update_result.get("Status"),
            "| Peak:",
            update_result.get("Peak Price"),
            "| P&L %:",
            update_result.get("Current Profit %"),
        )

        if update_result.get("Status") != "UPDATED":
            print("\nStage 4A update failed safely.")
            return

    print("\n" + "=" * 65)
    print("V16.2 STAGE 4A REAL-MARKET PAPER UPDATE: PASS")
    print("PAPER POSITION UPDATED — NO LIVE ORDER")
    print("=" * 65)


if __name__ == "__main__":
    main()
