"""
JKJ AI Trader
V16.2 Stage 3 — Real-Market to Paper Validation

Purpose:
Connect fresh V16.2 real-market observations to the
already validated V16.1 paper-entry qualification chain.

This test does NOT:
- place live orders
- connect to any live order API
- modify V12.1-V15
- modify main.py
"""

from modules.nifty_option_v16_2_real_market_sequence import (
    collect_real_market_sequence,
)

from modules.nifty_option_v16_real_market_paper_validation import (
    validate_real_market_paper_entry,
)


def main():

    print("\nJKJ AI Trader — V16.2 Stage 3")
    print("Real-Market to Paper Validation")
    print("=" * 65)

    sequence_result = collect_real_market_sequence(
        option_type="CE",
        observation_count=4,
        interval_seconds=10,
    )

    print("\nObservation Sequence Status:")
    print(sequence_result.get("Status"))

    if sequence_result.get("Status") != "SEQUENCE_RECORDED":
        print("\nStage 3 stopped safely.")
        print("Reason:")
        print(sequence_result.get("Reason"))
        return

    observations = sequence_result.get(
        "Observations",
        [],
    )

    print("\nTrading Symbol:")
    print(sequence_result.get("Trading Symbol"))

    print("Observation Count:")
    print(len(observations))

    validation_result = validate_real_market_paper_entry(
        observations=observations,
        quantity=75,
        trade_id="V16.2-REAL-TEST-001",
    )

    print("\nV16.1 Paper Entry Validation Result:")
    print(validation_result)

    status = validation_result.get("Status")

    if status == "PAPER_TRADE_OPENED":

        print("\n" + "=" * 65)
        print("V16.2 STAGE 3 REAL-MARKET TO PAPER: PASS")
        print("PAPER TRADE OPENED — NO LIVE ORDER")
        print("=" * 65)

    elif status in (
        "REJECTED",
        "INSUFFICIENT_OBSERVATIONS",
    ):

        print("\n" + "=" * 65)
        print("V16.2 STAGE 3 SAFE REJECTION: PASS")
        print("NO PAPER TRADE OPENED")
        print("=" * 65)

    else:

        print("\n" + "=" * 65)
        print("V16.2 STAGE 3: REVIEW REQUIRED")
        print("=" * 65)


if __name__ == "__main__":
    main()
