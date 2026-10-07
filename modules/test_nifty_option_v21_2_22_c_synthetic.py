"""
JKJ AI TRADER
V21.2.22-C Synthetic Validation

Tests:
    1. PERSISTENCE_SUPPORTED
    2. DEVELOPING_BUT_NOT_PERSISTENT
    3. EVIDENCE_CONFLICT
    4. INSUFFICIENT_EVIDENCE

No Zerodha connection.
No live orders.
No paper trades.
"""

from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)


SYMBOL_PERSISTENT = "NIFTY_TEST_PERSISTENT"
SYMBOL_DEVELOPING = "NIFTY_TEST_DEVELOPING"
SYMBOL_CONFLICT = "NIFTY_TEST_CONFLICT"
SYMBOL_INSUFFICIENT = "NIFTY_TEST_INSUFFICIENT"


def make_observations(prices):
    return [
        {
            "Status": "RECORDED",
            "Trading Symbol": "TEST",
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22500.0,
            "Option Type": "CE",
            "Current Price": price,
            "NIFTY Spot Price": 22500.0,
            "Volume": 1000.0 + (index * 500),
            "Open Interest": 50000.0,
            "Timestamp": f"2026-10-05T10:00:{index:02d}+05:30",
        }
        for index, price in enumerate(prices)
    ]


def make_qualification(
    symbol,
    lifecycle,
    qualification,
):
    return {
        "Status": "CANDIDATE_QUALIFIED",
        "Trading Symbol": symbol,
        "Lifecycle State": lifecycle,
        "Qualification": qualification,
        "Reason": "Synthetic validation candidate.",
        "Recent Movement %": 5.0,
        "Latest Velocity %/sec": 0.10,
        "Latest Acceleration %/sec2": 0.01,
        "Movement State": "ACCELERATING",
        "Latest Price": 110.0,
        "Observation Count": 4,
        "Peak Movement %": 10.0,
        "Giveback From Peak %": 0.0,
        "Current Recovery %": 0.0,
        "Maximum Recovery %": 0.0,
        "Live Order": False,
        "Paper Trade": False,
    }


def main():

    qualification_result = {
        "Status": "CANDIDATE_QUALIFICATION_COMPLETE",
        "Qualified Candidates": [
            make_qualification(
                SYMBOL_PERSISTENT,
                "STRENGTHENING",
                "STRONG_DEVELOPING_CANDIDATE",
            ),
            make_qualification(
                SYMBOL_DEVELOPING,
                "PERSISTING",
                "DEVELOPING_CANDIDATE",
            ),
            make_qualification(
                SYMBOL_CONFLICT,
                "PERSISTING",
                "DEVELOPING_CANDIDATE",
            ),
            make_qualification(
                SYMBOL_INSUFFICIENT,
                "PERSISTING",
                "DEVELOPING_CANDIDATE",
            ),
        ],
    }

    detailed_evidence = {
        "Status": "DETAILED_EVIDENCE_COMPLETE",
        "Observations": {
            # Continuously rising:
            # classical V12.6 persistence can be supported.
            SYMBOL_PERSISTENT: make_observations(
                [100.0, 102.0, 104.0, 106.0]
            ),

            # Overall positive, but first interval DOWN:
            # DOWN -> UP -> UP
            # therefore V12.6 is NOT_PERSISTENT.
            SYMBOL_DEVELOPING: make_observations(
                [100.0, 98.0, 103.0, 108.0]
            ),

            # Overall positive but latest movement DOWN:
            # should be treated as evidence conflict.
            SYMBOL_CONFLICT: make_observations(
                [100.0, 102.0, 105.0, 103.0]
            ),

            # Deliberately insufficient.
            SYMBOL_INSUFFICIENT: make_observations(
                [100.0, 102.0, 104.0]
            ),
        },
    }

    # This mirrors the actual V21.2.15 → V12.6
    # result structure used by the real pipeline.
    momentum_result = {
        "Status": "UNIFIED_MOMENTUM_COMPLETE",
        "Results": [
            {
                "Trading Symbol": SYMBOL_PERSISTENT,
                "Status": "CONFIRMED",
                "Momentum Sequence": {
                    "Persistence Status": "PERSISTENT",
                    "Direction": "UP",
                },
                "Momentum Confirmation": {
                    "Momentum Confirmation": "CONFIRMED",
                },
            },
            {
                "Trading Symbol": SYMBOL_DEVELOPING,
                "Status": "NOT_CONFIRMED",
                "Momentum Sequence": {
                    "Persistence Status": "NOT_PERSISTENT",
                    "Direction": "DOWN",
                },
                "Momentum Confirmation": {
                    "Momentum Confirmation": "NOT_CONFIRMED",
                },
            },
            {
                "Trading Symbol": SYMBOL_CONFLICT,
                "Status": "NOT_CONFIRMED",
                "Momentum Sequence": {
                    "Persistence Status": "NOT_PERSISTENT",
                    "Direction": "UP",
                },
                "Momentum Confirmation": {
                    "Momentum Confirmation": "NOT_CONFIRMED",
                },
            },
            {
                "Trading Symbol": SYMBOL_INSUFFICIENT,
                "Status": "NOT_CONFIRMED",
                "Momentum Sequence": {
                    "Persistence Status": "NOT_PERSISTENT",
                    "Direction": "UP",
                },
                "Momentum Confirmation": {
                    "Momentum Confirmation": "NOT_CONFIRMED",
                },
            },
        ],
    }

    result = reconcile_candidates(
        qualification_result,
        detailed_evidence,
        momentum_result,
    )

    print()
    print("=" * 75)
    print("V21.2.22-C SYNTHETIC VALIDATION")
    print("=" * 75)

    expected = {
        SYMBOL_PERSISTENT: "PERSISTENCE_SUPPORTED",
        SYMBOL_DEVELOPING: "DEVELOPING_BUT_NOT_PERSISTENT",
        SYMBOL_CONFLICT: "EVIDENCE_CONFLICT",
        SYMBOL_INSUFFICIENT: "INSUFFICIENT_EVIDENCE",
    }

    actual = {}

    for item in result.get("Candidates", []):
        symbol = item.get("Trading Symbol")
        reconciliation = item.get("Reconciliation")
        actual[symbol] = reconciliation

        print()
        print(f"Trading Symbol: {symbol}")
        print(
            f"Reconciliation: {reconciliation}"
        )
        print(
            f"Overall Movement: "
            f"{item.get('Overall Movement %')}"
        )
        print(
            f"Latest Movement: "
            f"{item.get('Latest Movement %')}"
        )
        print(
            f"V12.6 Persistence: "
            f"{item.get('V12.6 Persistence')}"
        )
        print(
            f"V12.6 Confirmation: "
            f"{item.get('V12.6 Confirmation')}"
        )
        print(
            f"Reason: {item.get('Reason')}"
        )

    print()
    print("Expected classifications:")
    print(expected)

    print()
    print("Actual classifications:")
    print(actual)

    classifications_pass = (
        actual == expected
    )

    safety_pass = (
        result.get("Live Order") is False
        and result.get("Paper Trade") is False
        and all(
            item.get("Live Order") is False
            and item.get("Paper Trade") is False
            for item in result.get("Candidates", [])
        )
    )

    if classifications_pass:
        print(
            "Classification Rules: PASS"
        )
    else:
        print(
            "Classification Rules: FAIL"
        )

    if safety_pass:
        print(
            "Safety: PASS"
        )
    else:
        print(
            "Safety: FAIL"
        )

    if classifications_pass and safety_pass:
        print()
        print(
            "V21.2.22-C SYNTHETIC TEST PASS"
        )
    else:
        print()
        print(
            "V21.2.22-C SYNTHETIC TEST FAIL"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
