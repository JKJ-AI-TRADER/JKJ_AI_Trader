from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    _build_record,
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

    prices = [100.00, 101.50, 103.50, 106.00]
    nifty = [22500.0, 22495.0, 22488.0, 22480.0]
    volume = [1000, 1200, 1500, 1900]
    oi = [50000, 50500, 51200, 52100]

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
        assert record["Status"] == "RECORDED"
        assert record["Trading Symbol"] == "NIFTY_TEST_22500CE"
        assert record["Underlying"] == "NIFTY"
        assert record["Expiry"] == "2026-10-06"
        assert record["Strike"] == 22500.0
        assert record["Option Type"] == "CE"
        assert record["Current Price"] == prices[i]
        assert record["NIFTY Spot Price"] == nifty[i]
        assert record["Volume"] == float(volume[i])
        assert record["Open Interest"] == float(oi[i])
        assert record["Timestamp"]

        observations.append(record)

    assert len(observations) == 4

    print()
    print("=" * 80)
    print("V21.2.22-B.2 SYNTHETIC VALIDATION")
    print("=" * 80)
    print("Status: PASS")
    print("Contract:", observations[0]["Trading Symbol"])
    print("Observation Count:", len(observations))
    print("Underlying:", observations[0]["Underlying"])
    print("Strike:", observations[0]["Strike"])
    print("Option Type:", observations[0]["Option Type"])
    print()
    print(
        "Price sequence:",
        [x["Current Price"] for x in observations],
    )
    print(
        "NIFTY sequence:",
        [x["NIFTY Spot Price"] for x in observations],
    )
    print(
        "Volume sequence:",
        [x["Volume"] for x in observations],
    )
    print(
        "OI sequence:",
        [x["Open Interest"] for x in observations],
    )
    print()
    print("V12.4-compatible required fields: PASS")
    print(
        "Safety: LIVE_ORDER=False | PAPER_TRADE=False"
    )


if __name__ == "__main__":
    main()
