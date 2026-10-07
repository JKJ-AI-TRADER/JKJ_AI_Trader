from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    _build_record,
)

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)


def main():

    candidate = {
        "Trading Symbol": "NIFTY_TEST_22500CE",
        "Selection Rank": 1,
        "Category": "CURRENT_DEVELOPING",
        "Lifecycle State": "STRENGTHENING",
    }

    instrument = {
        "tradingsymbol": "NIFTY_TEST_22500CE",
        "instrument_token": 123456,
        "name": "NIFTY",
        "expiry": "2026-10-06",
        "strike": 22500.0,
        "instrument_type": "CE",
    }

    prices = [
        100.00,
        101.50,
        103.50,
        106.00,
    ]

    nifty = [
        22500.0,
        22495.0,
        22488.0,
        22480.0,
    ]

    volume = [
        1000,
        1200,
        1500,
        1900,
    ]

    oi = [
        50000,
        50500,
        51200,
        52100,
    ]

    observations = []

    for i in range(4):

        normalized_quote = {
            "Current Price": prices[i],
            "Previous Close": 99.0,
            "Volume": volume[i],
            "Open Interest": oi[i],
            "Last Trade Time": (
                f"2026-10-05T09:15:{i * 10:02d}"
            ),
        }

        record, reason = _build_record(
            candidate,
            instrument,
            normalized_quote,
            nifty[i],
        )

        assert record is not None, reason

        observations.append(record)

    identity = (
        "NIFTY_TEST_22500CE",
        "NIFTY",
        "2026-10-06",
        22500.0,
        "CE",
    )

    unified_observation = {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",
        "Observation Count": 4,
        "Movement Intervals": 3,
        "Observations By Contract": {
            identity: observations,
        },
        "Live Order": False,
        "Paper Trade": False,
    }

    result = evaluate_unified_observation_momentum(
        unified_observation
    )

    print()
    print("=" * 90)
    print(
        "V21.2.22-B.2 → V21.2.15 → V12.6 "
        "SYNTHETIC VALIDATION"
    )
    print("=" * 90)

    print(
        "Overall Status:",
        result.get("Status"),
    )

    print(
        "Observation Count:",
        result.get("Observation Count"),
    )

    print(
        "Movement Intervals:",
        result.get("Movement Intervals"),
    )

    print(
        "Contract Count:",
        result.get("Contract Count"),
    )

    for item in result.get("Results", []):

        print()
        print(
            "Trading Symbol:",
            item.get("Trading Symbol"),
        )

        print(
            "Option Type:",
            item.get("Option Type"),
        )

        print(
            "Status:",
            item.get("Status"),
        )

        print(
            "Observation Count:",
            item.get("Observation Count"),
        )

        print(
            "Movement Intervals:",
            item.get("Movement Intervals"),
        )

        sequence = item.get(
            "Momentum Sequence"
        )

        if isinstance(sequence, dict):
            print(
                "Persistence:",
                sequence.get(
                    "Persistence Status"
                ),
            )

            print(
                "Direction:",
                sequence.get("Direction"),
            )

        confirmation = item.get(
            "Momentum Confirmation"
        )

        if isinstance(confirmation, dict):
            print(
                "Momentum Confirmation:",
                confirmation.get(
                    "Momentum Confirmation"
                ),
            )

    print()

    print(
        "Safety:",
        "LIVE_ORDER=False | PAPER_TRADE=False",
    )

    assert result.get("Status") == (
        "UNIFIED_MOMENTUM_COMPLETE"
    )

    assert result.get("Observation Count") == 4

    assert result.get("Contract Count") == 1

    assert len(result.get("Results", [])) == 1

    print()
    print(
        "V21.2.22-B.2 → V21.2.15 → V12.6 "
        "SYNTHETIC TEST PASS"
    )


if __name__ == "__main__":
    main()
