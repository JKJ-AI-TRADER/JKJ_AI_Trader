"""
JKJ AI Trader
V21.2.23.4 - Discovery → V21.2.19 Lifecycle Adapter

Purpose:
Convert V21.2.23 deep-observation history into the existing
V21.2.19 lifecycle analysis path.

Architecture:
V21.2.23 Discovery
    ↓
V21.2.23.1 Candidate Selection
    ↓
V21.2.23.2 Early Entry Observation
    ↓
V21.2.23.3 Underlying Confirmation
    ↓
V21.2.23.4 This Adapter
    ↓
Existing V21.2.18.5.3 Observation Store
    ↓
Existing V21.2.18.5.4 Movement Analyzer
    ↓
Existing V21.2.19 Candidate Lifecycle

Important:
- This module does NOT assign lifecycle states.
- This module does NOT calculate velocity.
- This module does NOT calculate acceleration.
- This module does NOT qualify candidates.
- This module does NOT generate BUY/SELL.
- This module does NOT place orders.
"""

from __future__ import annotations

from typing import Any, Dict, List

from modules.nifty_option_v21_2_18_5_3_intraday_observation_store import (
    create_intraday_observation_store,
    record_scan_observations,
)

from modules.nifty_option_v21_2_18_5_4_intraday_movement_analyzer import (
    analyze_intraday_store,
)

from modules.nifty_option_v21_2_19_candidate_lifecycle import (
    update_candidate_lifecycle,
)


LIVE_ORDER = False
PAPER_TRADE = False


def _safe_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _extract_observations(
    early_entry_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract V21.2.23.2 observation records.

    V21.2.23.2 stores detailed records under
    "Observation History" as one list per observation cycle.
    Flatten those real records for the existing JKJ observation
    store. No observations are invented or reconstructed.
    """

    if not isinstance(early_entry_result, dict):
        return []

    observation_history = early_entry_result.get(
        "Observation History",
        [],
    )

    if not isinstance(observation_history, list):
        return []

    observations: List[Dict[str, Any]] = []

    for cycle in observation_history:
        if not isinstance(cycle, list):
            continue

        for observation in cycle:
            if isinstance(observation, dict):
                observations.append(observation)

    return observations

def _confirmed_symbols(
    confirmation_result: Dict[str, Any],
) -> set[str]:
    """
    Return symbols explicitly confirmed by V21.2.23.3.

    Confirmation is used only as a promotion restriction.
    It does NOT become a lifecycle state.
    """

    if not isinstance(confirmation_result, dict):
        return set()

    confirmed = confirmation_result.get(
        "Confirmed Candidates",
        [],
    )

    symbols: set[str] = set()

    for candidate in _safe_list(confirmed):
        symbol = candidate.get("Trading Symbol")

        if symbol:
            symbols.add(str(symbol))

    return symbols


def _build_scan_result(
    observations: List[Dict[str, Any]],
    allowed_symbols: set[str] | None = None,
) -> Dict[str, Any]:
    """
    Convert V21.2.23 observations into the existing
    observation-store scan-result contract.

    Existing fields are preserved.

    No lifecycle state is added.
    """

    results: List[Dict[str, Any]] = []

    for observation in observations:

        symbol = observation.get("Trading Symbol")

        if not symbol:
            continue

        if (
            allowed_symbols is not None
            and symbol not in allowed_symbols
        ):
            continue

        item = dict(observation)

        # The existing movement analyzer requires the latest
        # market price. V21.2.23 already supplies Latest Price.
        if item.get("Latest Price") is None:
            continue

        results.append(item)

    return {
        "Results": results,
    }


def adapt_discovery_to_lifecycle(
    early_entry_result: Dict[str, Any],
    confirmation_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Adapt V21.2.23 observation history into the existing
    V21.2.19 lifecycle-analysis contract.

    Confirmation result is optional.

    When supplied, only candidates explicitly confirmed by
    V21.2.23.3 are promoted into the lifecycle observation path.

    The lifecycle engine itself remains authoritative.
    """

    if not isinstance(early_entry_result, dict):
        return {
            "Status": "DISCOVERY_LIFECYCLE_ADAPTER_REJECTED",
            "Reason": "Invalid V21.2.23.2 result.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    # Preserve the original V21.2.23 observation-cycle
    # timestamps. Do NOT flatten all cycles into one scan,
    # because record_scan_observations() assigns one timestamp
    # to every item in a scan.
    observation_history = early_entry_result.get(
        "Observation History",
        [],
    )

    if not isinstance(observation_history, list):
        observation_history = []

    observation_cycles: List[List[Dict[str, Any]]] = []

    for cycle in observation_history:
        if not isinstance(cycle, list):
            continue

        valid_cycle = [
            item
            for item in cycle
            if isinstance(item, dict)
            and item.get("Trading Symbol")
            and item.get("Latest Price") is not None
        ]

        if valid_cycle:
            observation_cycles.append(valid_cycle)

    if not observation_cycles:
        return {
            "Status": "DISCOVERY_LIFECYCLE_ADAPTER_REJECTED",
            "Reason": "No V21.2.23 observations available.",
            "Observation Count": 0,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    allowed_symbols = None

    if confirmation_result is not None:

        if not isinstance(
            confirmation_result,
            dict,
        ):
            return {
                "Status": "DISCOVERY_LIFECYCLE_ADAPTER_REJECTED",
                "Reason": "Invalid V21.2.23.3 confirmation result.",
                "Live Order": LIVE_ORDER,
                "Paper Trade": PAPER_TRADE,
            }

        if (
            confirmation_result.get("Status")
            != "UNDERLYING_CONFIRMATION_GATE_COMPLETE"
        ):
            return {
                "Status": "DISCOVERY_LIFECYCLE_ADAPTER_REJECTED",
                "Reason": (
                    "V21.2.23.3 confirmation gate "
                    "was not complete."
                ),
                "Live Order": LIVE_ORDER,
                "Paper Trade": PAPER_TRADE,
            }

        allowed_symbols = _confirmed_symbols(
            confirmation_result
        )

    store = create_intraday_observation_store()

    store_results = []

    for cycle in observation_cycles:
        scan_result = _build_scan_result(
            cycle,
            allowed_symbols,
        )

        if not scan_result.get("Results"):
            continue

        # The shared observation store assigns one fresh timestamp
        # to a scan. For V21.2.23.2 we already have genuine
        # observation timestamps, so restore those timestamps
        # immediately after recording the cycle.
        original_timestamps = {
            str(item.get("Trading Symbol")): item.get(
                "Observation Timestamp"
            )
            for item in scan_result.get("Results", [])
            if item.get("Trading Symbol")
            and item.get("Observation Timestamp")
        }

        store_result = record_scan_observations(
            store,
            scan_result,
        )

        for symbol, timestamp in original_timestamps.items():
            if (
                symbol in store
                and store[symbol]
                and timestamp
            ):
                store[symbol][-1]["Observation Timestamp"] = (
                    timestamp
                )

        store_results.append(store_result)

    if not store:
        return {
            "Status": "DISCOVERY_LIFECYCLE_ADAPTER_REJECTED",
            "Reason": (
                "No valid observations remained after "
                "adapter filtering."
            ),
            "Store Results": store_results,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    # IMPORTANT:
    # Existing JKJ movement mathematics is reused here.
    # No velocity/acceleration calculations are duplicated.
    analysis = analyze_intraday_store(store)

    lifecycle_store: Dict[str, Dict[str, Any]] = {}

    # IMPORTANT:
    # Existing V21.2.19 lifecycle engine decides the lifecycle state.
    # This adapter does not assign PERSISTING/STRENGTHENING/etc.
    lifecycle_store = update_candidate_lifecycle(
        lifecycle_store,
        analysis,
    )

    return {
        "Status": "DISCOVERY_TO_LIFECYCLE_ADAPTER_COMPLETE",
        "Observation Count": sum(
            len(items)
            for items in store.values()
        ),
        "Observation Cycle Count": len(
            observation_cycles
        ),
        "Tracked Symbols": len(store),
        "Analysis": analysis,
        "Observation Store": store,
        "Lifecycle Store": lifecycle_store,
        "Confirmation Filter Applied": (
            confirmation_result is not None
        ),
        "Confirmed Symbol Count": (
            len(allowed_symbols)
            if allowed_symbols is not None
            else None
        ),
        "Source": (
            "V21.2.23.2/23.3 → Existing "
            "V21.2.18.5.3/5.4 → V21.2.19"
        ),
        "Lifecycle State Assigned By":
            "Existing V21.2.19 Lifecycle Engine",
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def _synthetic_test() -> None:
    """
    Deterministic adapter test.

    Uses synthetic observations only.
    No Zerodha connection.
    No orders.
    """

    symbol = "TESTCE"

    early_entry_result = {
        "Status": "EARLY_ENTRY_OBSERVATION_COMPLETE",
        "Observations": [
            {
                "Trading Symbol": symbol,
                "Option Type": "CE",
                "Strike": 23000,
                "Expiry": "2026-10-06",
                "9:15 Price": 100.0,
                "Latest Price": 100.0,
                "Observation Timestamp":
                    "2026-10-06T09:15:00",
            },
            {
                "Trading Symbol": symbol,
                "Option Type": "CE",
                "Strike": 23000,
                "Expiry": "2026-10-06",
                "9:15 Price": 100.0,
                "Latest Price": 101.0,
                "Observation Timestamp":
                    "2026-10-06T09:15:15",
            },
            {
                "Trading Symbol": symbol,
                "Option Type": "CE",
                "Strike": 23000,
                "Expiry": "2026-10-06",
                "9:15 Price": 100.0,
                "Latest Price": 103.0,
                "Observation Timestamp":
                    "2026-10-06T09:15:30",
            },
            {
                "Trading Symbol": symbol,
                "Option Type": "CE",
                "Strike": 23000,
                "Expiry": "2026-10-06",
                "9:15 Price": 100.0,
                "Latest Price": 106.0,
                "Observation Timestamp":
                    "2026-10-06T09:15:45",
            },
        ],
        "Live Order": False,
        "Paper Trade": False,
    }

    confirmation_result = {
        "Status":
            "UNDERLYING_CONFIRMATION_GATE_COMPLETE",
        "Confirmed Candidates": [
            {
                "Trading Symbol": symbol,
                "Option Type": "CE",
            }
        ],
        "Rejected Candidates": [],
        "Live Order": False,
        "Paper Trade": False,
    }

    result = adapt_discovery_to_lifecycle(
        early_entry_result,
        confirmation_result,
    )

    assert (
        result["Status"]
        == "DISCOVERY_TO_LIFECYCLE_ADAPTER_COMPLETE"
    )

    assert result["Tracked Symbols"] == 1
    assert result["Observation Count"] == 4

    assert symbol in result["Analysis"]
    assert symbol in result["Lifecycle Store"]

    assert result["Live Order"] is False
    assert result["Paper Trade"] is False

    lifecycle = result["Lifecycle Store"][symbol]

    assert lifecycle.get("Trading Symbol") == symbol
    assert lifecycle.get("Latest", {}).get("Observation Count") == 4

    # The adapter must never manufacture a lifecycle state.
    # It must come from the existing lifecycle engine.
    assert lifecycle.get("State") in {
        "NEW",
        "WATCHING",
        "PERSISTING",
        "STRENGTHENING",
        "MOMENTUM_SHIFT_UP",
        "MOMENTUM_SHIFT_DOWN",
        "WEAKENING",
        "PEAK",
        "RETREAT",
        "DROPPED",
    }

    print()
    print("=" * 70)
    print(
        "V21.2.23.4 DISCOVERY → LIFECYCLE ADAPTER TEST"
    )
    print("=" * 70)
    print("Status:", result["Status"])
    print("Tracked Symbols:", result["Tracked Symbols"])
    print("Observation Count:", result["Observation Count"])
    print(
        "Lifecycle State:",
        lifecycle.get("State"),
    )
    print(
        "State Assigned By:",
        result["Lifecycle State Assigned By"],
    )
    print("Live Order:", result["Live Order"])
    print("Paper Trade:", result["Paper Trade"])
    print()
    print(
        "V21.2.23.4 DISCOVERY → LIFECYCLE "
        "ADAPTER TEST: PASS"
    )


if __name__ == "__main__":
    _synthetic_test()
