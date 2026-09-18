"""
JKJ AI Trader
V16.2 Stage 2 — Real-Market Observation Sequence Test

This test does NOT:
- place live orders
- make BUY/SELL decisions
- create paper trades
"""

import os

from modules.nifty_option_v16_2_real_market_sequence import (
    collect_real_market_sequence,
)

from modules.nifty_option_observation_storage import (
    OBSERVATION_FILE,
)


def main():

    print("\nJKJ AI Trader — V16.2 Stage 2")
    print("Real-Market Observation Sequence")
    print("=" * 60)

    result = collect_real_market_sequence(
        option_type="CE",
        observation_count=4,
        interval_seconds=10,
    )

    print("\nSequence Status:")
    print(result.get("Status"))

    print("Trading Symbol:")
    print(result.get("Trading Symbol"))

    print("Observation Count:")
    print(result.get("Observation Count"))

    if result.get("Status") == "SEQUENCE_RECORDED":

        assert result.get("Observation Count") == 4
        assert len(result.get("Observations", [])) == 4

        symbols = {
            observation.get("Trading Symbol")
            for observation in result.get(
                "Observations",
                [],
            )
        }

        assert len(symbols) == 1

        assert os.path.isfile(
            OBSERVATION_FILE
        )

        print("\n" + "=" * 60)
        print("V16.2 STAGE 2 REAL-MARKET SEQUENCE: PASS")
        print("=" * 60)

    else:

        print("\nReason:")
        print(result.get("Reason"))

        print("\n" + "=" * 60)
        print("V16.2 STAGE 2 REAL-MARKET SEQUENCE: FAILED")
        print("=" * 60)


if __name__ == "__main__":
    main()
