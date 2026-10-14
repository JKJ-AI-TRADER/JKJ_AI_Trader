"""
JKJ AI Trader
V21.2.17 — Offline Interface Test

Uses the exact V21.2.15 observation identity structure.

No Zerodha connection.
No market observations.
No live orders.
No paper trades.
"""

from modules.nifty_option_v21_2_17_risk_stop_targets import (
    evaluate_real_market_risk_stop_targets,
)


def main():

    trading_symbol = "NIFTY26SEP23100CE"
    underlying = "NIFTY"
    expiry = "2026-09-29"
    strike = 23100.0
    option_type = "CE"

    observation_identity = (
        trading_symbol,
        underlying,
        expiry,
        strike,
        option_type,
    )

    decision_entry_result = {
        "Status": "DECISION_ENTRY_COMPLETE",
        "Contract Count": 1,
        "Results": [
            {
                "Status": "DECISION_ENTRY_EVALUATED",
                "Trading Symbol": trading_symbol,
                "Underlying": underlying,
                "Expiry": expiry,
                "Strike": strike,
                "Option Type": option_type,
                "Option Direction": "UP",
                "Momentum Confirmation": "CONFIRMED",
                "Market Context": "MOVING_TOGETHER",
                "Movement Relationship": "MOVING_TOGETHER",
                "Momentum Context": "SUPPORTED",
                "Opportunity Classification": (
                    "SUPPORTED_OPPORTUNITY"
                ),
                "Opportunity Strength": "STRONG",
                "Risk Classification": "LOWER_RISK_CONTEXT",
                "Trade Quality": "HIGH_QUALITY_CONTEXT",
                "Entry Qualification": "ENTRY_QUALIFIED",

                "Entry Qualification Result": {
                    "Status": "QUALIFIED",
                    "Trading Symbol": trading_symbol,
                    "Underlying": underlying,
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Option Direction": "UP",
                    "Momentum Confirmation": "CONFIRMED",
                    "Market Context": "MOVING_TOGETHER",
                    "Movement Relationship": "MOVING_TOGETHER",
                    "Momentum Context": "SUPPORTED",
                    "Opportunity Classification": (
                        "SUPPORTED_OPPORTUNITY"
                    ),
                    "Opportunity Strength": "STRONG",
                    "Risk Classification": "LOWER_RISK_CONTEXT",
                    "Trade Quality": "HIGH_QUALITY_CONTEXT",
                    "Entry Qualification": "ENTRY_QUALIFIED",
                },
            }
        ],
        "New Market Observations": False,
        "Live Order": False,
        "Paper Trade": False,
    }

    unified_observation_result = {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",
        "Observation Count": 4,
        "Movement Intervals": 3,
        "Interval Seconds": 10,
        "Contract Count": 1,

        "Observations By Contract": {
            observation_identity: [
                {
                    "Status": "RECORDED",
                    "Trading Symbol": trading_symbol,
                    "Underlying": underlying,
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Current Price": 120.0,
                },
                {
                    "Status": "RECORDED",
                    "Trading Symbol": trading_symbol,
                    "Underlying": underlying,
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Current Price": 121.0,
                },
                {
                    "Status": "RECORDED",
                    "Trading Symbol": trading_symbol,
                    "Underlying": underlying,
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Current Price": 119.0,
                },
                {
                    "Status": "RECORDED",
                    "Trading Symbol": trading_symbol,
                    "Underlying": underlying,
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Current Price": 122.0,
                },
            ]
        },

        "Live Order": False,
        "Paper Trade": False,
    }

    result = evaluate_real_market_risk_stop_targets(
        decision_entry_result,
        unified_observation_result,
    )

    # Offline regression: invalid observations must be rejected safely.
    import copy

    for invalid_price in (
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ):
        invalid_input = copy.deepcopy(unified_observation_result)
        invalid_input["Observations By Contract"][
            observation_identity
        ][0]["Current Price"] = invalid_price

        rejected = evaluate_real_market_risk_stop_targets(
            decision_entry_result,
            invalid_input,
        )

        assert rejected["Results"][0]["Status"] == (
            "RISK_STOP_TARGETS_REJECTED"
        ), (repr(invalid_price), rejected)

        assert rejected["Live Order"] is False
        assert rejected["Paper Trade"] is False

    print("Invalid observation regression cases: PASS")

    print()
    print("=" * 70)
    print("V21.2.17 OFFLINE RISK + STOP + TARGET TEST")
    print("=" * 70)

    print("Status:", result.get("Status"))
    print("Contract Count:", result.get("Contract Count"))
    print(
        "New Market Observations:",
        result.get("New Market Observations"),
    )
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))

    print()

    for item in result.get("Results", []):

        print(
            "Trading Symbol:",
            item.get("Trading Symbol"),
        )
        print("Status:", item.get("Status"))
        print(
            "Entry Qualification:",
            item.get("Entry Qualification"),
        )
        print(
            "Entry Risk Context:",
            item.get("Entry Risk Context"),
        )
        print(
            "Stop-Loss Context:",
            item.get("Stop-Loss Context"),
        )
        print(
            "Price History:",
            item.get("Price History"),
        )
        print(
            "Entry Price:",
            item.get("Entry Price"),
        )
        print(
            "Structural Low:",
            item.get("Structural Low"),
        )
        print(
            "Stop Price:",
            item.get("Stop Price"),
        )
        print(
            "Stop Distance:",
            item.get("Stop Distance"),
        )
        print("Target 1:", item.get("Target 1"))
        print("Target 2:", item.get("Target 2"))
        print("Target 3:", item.get("Target 3"))

        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
