"""
JKJ AI Trader
V16.2 Stage 1 — Real-Market Observation Test

This test does NOT:
- place live orders
- make BUY/SELL decisions
- create paper trades
"""

from modules.nifty_option_v16_2_real_market_observer import (
    collect_real_market_observation,
)


def main():

    print("\nJKJ AI Trader — V16.2 Stage 1")
    print("Real-Market Option Observation")
    print("=" * 55)

    result = collect_real_market_observation(
        option_type="CE",
    )

    print("\nV16.2 Result:")
    print(result)

    if result.get("Status") == "RECORDED":

        print("\n" + "=" * 55)
        print("V16.2 STAGE 1 REAL-MARKET OBSERVATION: PASS")
        print("=" * 55)

    else:

        print("\n" + "=" * 55)
        print("V16.2 STAGE 1 REAL-MARKET OBSERVATION: FAILED")
        print("=" * 55)


if __name__ == "__main__":
    main()
