"""
JKJ AI TRADER V21.2.19-R
Recovery Intelligence

Observation-only analysis of candidate recovery patterns.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO ENTRY SIGNALS
- NO FIXED PROFIT TARGET
"""

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MIN_RECOVERY_FOR_DISPLAY = 0.50


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _latest_observation(record: Dict[str, Any]) -> Dict[str, Any]:
    observations = record.get("Observations") or []
    if not observations:
        return {}
    return observations[-1]


def build_recovery_candidates(
    lifecycle_store: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Identify candidates that have recovered from their lowest
    observed movement.

    This is measurement only. It does not decide whether to trade.
    """

    candidates: List[Dict[str, Any]] = []

    for symbol, record in lifecycle_store.items():
        latest = _latest_observation(record)

        if not latest:
            continue

        lowest_movement = record.get("Lowest Movement %")
        current_recovery = _to_float(
            record.get("Current Recovery %"), 0.0
        )
        maximum_recovery = _to_float(
            record.get("Maximum Recovery %"), 0.0
        )

        if lowest_movement is None:
            continue

        lowest_movement = _to_float(lowest_movement)

        # True recovery requires the candidate to have first
        # moved below 0% and then recovered upward.
        if lowest_movement >= 0.0:
            continue

        if current_recovery < MIN_RECOVERY_FOR_DISPLAY:
            continue

        latest_movement = _to_float(
            latest.get("Recent Movement %"), 0.0
        )
        velocity = _to_float(
            latest.get("Latest Velocity %/sec"), 0.0
        )
        acceleration = _to_float(
            latest.get("Latest Acceleration %/sec2"), 0.0
        )

        candidates.append(
            {
                "Trading Symbol": symbol,
                "State": record.get("State", "UNKNOWN"),
                "Lowest Movement %": lowest_movement,
                "Current Movement %": latest_movement,
                "Current Recovery %": current_recovery,
                "Maximum Recovery %": maximum_recovery,
                "Velocity %/sec": velocity,
                "Acceleration %/sec²": acceleration,
                "Recovery Start Observation":
                    record.get("Recovery Start Observation"),
                "Recovery Duration Observations":
                    record.get("Recovery Duration Observations", 0),
                "Lowest Observation":
                    record.get("Lowest Observation"),
                "Lowest Price":
                    record.get("Lowest Price"),
                "Current Price":
                    latest.get("Latest Price"),
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    candidates.sort(
        key=lambda item: item["Current Recovery %"],
        reverse=True,
    )

    return candidates


def print_recovery_candidates(
    lifecycle_store: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    candidates = build_recovery_candidates(lifecycle_store)

    print("\n" + "=" * 78)
    print("RECOVERY INTELLIGENCE")
    print("=" * 78)

    if not candidates:
        print("No active recovery candidates detected.")
        print("Safety: LIVE ORDER=False | PAPER TRADE=False")
        return candidates

    print(
        f"{'Trading Symbol':<24}"
        f"{'Low %':>9}"
        f"{'Current %':>11}"
        f"{'Recovery %':>12}"
        f"{'Velocity':>12}"
        f"{'Accel':>12}"
    )
    print("-" * 78)

    for item in candidates:
        print(
            f"{item['Trading Symbol']:<24}"
            f"{item['Lowest Movement %']:>9.2f}"
            f"{item['Current Movement %']:>11.2f}"
            f"{item['Current Recovery %']:>12.2f}"
            f"{item['Velocity %/sec']:>12.5f}"
            f"{item['Acceleration %/sec²']:>12.5f}"
        )

    print("-" * 78)
    print(
        f"Recovery candidates: {len(candidates)}"
    )
    print("No fixed profit target is applied.")
    print("Safety: LIVE ORDER=False | PAPER TRADE=False")

    return candidates


if __name__ == "__main__":
    print(
        "JKJ V21.2.19 Recovery Intelligence "
        "is an analysis module."
    )
    print("It must be called with lifecycle data.")
