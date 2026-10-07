"""
JKJ AI TRADER V21.2.19-RJ
Recovery Journey Tracker

Observation-only measurement of genuine negative-to-recovery journeys.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO ENTRY SIGNALS
- NO FIXED PROFIT TARGET
"""

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def update_recovery_journey(
    journey_store: Dict[str, Dict[str, Any]],
    recovery_candidates: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Record the progression of genuine recovery candidates.

    This function measures behaviour only. It does not generate
    an entry, exit, buy, sell, or profit signal.
    """

    for candidate in recovery_candidates:
        symbol = candidate.get("Trading Symbol")
        if not symbol:
            continue

        lowest_movement = _to_float(
            candidate.get("Lowest Movement %")
        )
        current_movement = _to_float(
            candidate.get("Current Movement %")
        )
        current_recovery = _to_float(
            candidate.get("Current Recovery %")
        )
        velocity = _to_float(
            candidate.get("Velocity %/sec")
        )
        acceleration = _to_float(
            candidate.get("Acceleration %/sec²")
        )

        if symbol not in journey_store:
            journey_store[symbol] = {
                "Trading Symbol": symbol,
                "Lowest Movement %": lowest_movement,
                "Maximum Recovery %": current_recovery,
                "Current Recovery %": current_recovery,
                "Current Movement %": current_movement,
                "Recovery Start Observation": None,
                "Recovery Start Movement %": None,
                "Maximum Recovery Observation": None,
                "Last Observation": None,
                "Journey State": "RECOVERING",
                "Observations": [],
                "Live Order": False,
                "Paper Trade": False,
            }

        record = journey_store[symbol]

        observation_number = len(record["Observations"]) + 1

        # Preserve the lowest observed movement.
        record["Lowest Movement %"] = min(
            _to_float(record.get("Lowest Movement %")),
            lowest_movement,
        )

        # First point at which recovery is visible.
        if (
            record.get("Recovery Start Observation") is None
            and current_recovery > 0
        ):
            record["Recovery Start Observation"] = observation_number
            record["Recovery Start Movement %"] = current_movement

        # Track maximum recovery reached.
        previous_max = _to_float(
            record.get("Maximum Recovery %")
        )

        if current_recovery > previous_max:
            record["Maximum Recovery %"] = current_recovery
            record["Maximum Recovery Observation"] = observation_number

        record["Current Recovery %"] = current_recovery
        record["Current Movement %"] = current_movement
        record["Last Observation"] = observation_number

        record["Observations"].append(
            {
                "Observation": observation_number,
                "Current Movement %": current_movement,
                "Current Recovery %": current_recovery,
                "Velocity %/sec": velocity,
                "Acceleration %/sec²": acceleration,
            }
        )

        # Simple descriptive journey state.
        if (
            current_recovery > 0
            and velocity > 0
            and acceleration > 0
        ):
            record["Journey State"] = "RECOVERY_STRENGTHENING"
        elif current_recovery > 0 and velocity > 0:
            record["Journey State"] = "RECOVERY_CONTINUING"
        elif current_recovery > 0:
            record["Journey State"] = "RECOVERY_WEAKENING"
        else:
            record["Journey State"] = "RECOVERY_STALLED"

    return journey_store


def print_recovery_journey(
    journey_store: Dict[str, Dict[str, Any]],
) -> None:
    print("\n" + "=" * 125)
    print("RECOVERY JOURNEY TRACKER")
    print("=" * 125)

    if not journey_store:
        print("No recovery journeys recorded.")
        print("Safety: LIVE ORDER=False | PAPER TRADE=False")
        return

    records = sorted(
        journey_store.values(),
        key=lambda item: _to_float(
            item.get("Maximum Recovery %")
        ),
        reverse=True,
    )

    print(
        f"{'Trading Symbol':<24}"
        f"{'Low %':>8}"
        f"{'Current %':>10}"
        f"{'Current Rec.':>13}"
        f"{'Max Rec.':>11}"
        f"{'Start':>8}"
        f"{'Max Obs':>9}"
        f"{'Duration':>10}"
        f"{'Giveback':>10}"
        f"{'State':>22}"
    )
    print("-" * 125)

    for record in records:
        maximum_recovery = _to_float(
            record.get("Maximum Recovery %")
        )
        current_recovery = _to_float(
            record.get("Current Recovery %")
        )

        giveback = max(
            0.0,
            maximum_recovery - current_recovery,
        )

        recovery_start = record.get(
            "Recovery Start Observation"
        )
        maximum_observation = record.get(
            "Maximum Recovery Observation"
        )

        if (
            recovery_start is not None
            and maximum_observation is not None
        ):
            recovery_duration = (
                maximum_observation
                - recovery_start
            )
        else:
            recovery_duration = 0

        print(
            f"{record['Trading Symbol']:<24}"
            f"{_to_float(record.get('Lowest Movement %')):>8.2f}"
            f"{_to_float(record.get('Current Movement %')):>10.2f}"
            f"{current_recovery:>13.2f}"
            f"{maximum_recovery:>11.2f}"
            f"{str(recovery_start):>8}"
            f"{str(maximum_observation):>9}"
            f"{recovery_duration:>10}"
            f"{giveback:>10.2f}"
            f"{record.get('Journey State', 'UNKNOWN'):>22}"
        )

    print("-" * 125)
    print(f"Recovery journeys tracked: {len(records)}")
    print("Recovery Start → Maximum Recovery → Duration → Giveback are observation metrics only.")
    print("No fixed profit target is applied.")
    print("Safety: LIVE ORDER=False | PAPER TRADE=False")


def get_recovery_journey_summary(
    journey_store: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Return a descriptive summary of each recorded recovery journey.

    Observation only. No trading decision is generated.
    """

    summaries = []

    for record in journey_store.values():
        maximum_recovery = _to_float(
            record.get("Maximum Recovery %")
        )
        current_recovery = _to_float(
            record.get("Current Recovery %")
        )

        giveback = max(
            0.0,
            maximum_recovery - current_recovery,
        )

        recovery_start = record.get(
            "Recovery Start Observation"
        )
        maximum_observation = record.get(
            "Maximum Recovery Observation"
        )

        if (
            recovery_start is not None
            and maximum_observation is not None
        ):
            recovery_duration = (
                maximum_observation
                - recovery_start
            )
        else:
            recovery_duration = 0

        summaries.append(
            {
                "Trading Symbol": record.get(
                    "Trading Symbol"
                ),
                "Lowest Movement %": _to_float(
                    record.get("Lowest Movement %")
                ),
                "Current Movement %": _to_float(
                    record.get("Current Movement %")
                ),
                "Current Recovery %": current_recovery,
                "Maximum Recovery %": maximum_recovery,
                "Giveback From Maximum Recovery %": giveback,
                "Recovery Start Observation": recovery_start,
                "Maximum Recovery Observation": maximum_observation,
                "Recovery Duration Observations": recovery_duration,
                "Journey State": record.get(
                    "Journey State",
                    "UNKNOWN",
                ),
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    return sorted(
        summaries,
        key=lambda item: item[
            "Maximum Recovery %"
        ],
        reverse=True,
    )
