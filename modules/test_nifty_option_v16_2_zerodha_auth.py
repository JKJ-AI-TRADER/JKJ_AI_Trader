"""
JKJ AI Trader
V16.2 — Zerodha Authentication Test

This test does NOT:
- place live orders
- fetch market data
- make trading decisions
- create paper trades
"""

from modules.nifty_option_v16_2_zerodha_auth import (
    get_authenticated_kite,
)


def main():

    print("\nJKJ AI Trader — V16.2 Zerodha Authentication Test")
    print("=" * 55)

    result = get_authenticated_kite()

    print("\nAuthentication Status:")
    print(result.get("Status"))

    if result.get("Status") == "AUTHENTICATED":

        print("\n" + "=" * 55)
        print("V16.2 ZERODHA AUTHENTICATION: PASS")
        print("=" * 55)

    else:

        print("\nReason:")
        print(result.get("Reason"))

        print("\n" + "=" * 55)
        print("V16.2 ZERODHA AUTHENTICATION: FAILED")
        print("=" * 55)


if __name__ == "__main__":
    main()
