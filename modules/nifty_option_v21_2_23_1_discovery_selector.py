"""
JKJ AI Trader
V21.2.23.1 Discovery Candidate Selector

Purpose:
- Reduce broad V21.2.23 discovery results to a small number
  of strongest developing movers.
- Preserve discovery evidence for downstream deep observation.
- Candidate selection only.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO BUY / SELL
- NO ENTRY DECISION
- NO STOP / TARGET
- NO POSITION SIZING
"""

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_MAX_SELECTED = 10


def select_discovery_candidates(
    discovery_result: Dict[str, Any],
    max_selected: int = DEFAULT_MAX_SELECTED,
) -> Dict[str, Any]:
    """
    Select the strongest developing movers from V21.2.23.

    Selection is based on:
    1. Discovery State = DEVELOPING
    2. Positive movement
    3. Positive acceleration
    4. Stronger acceleration first
    5. Stronger movement second
    6. Symbol as deterministic tie-breaker

    This does NOT qualify an entry or trade.
    """

    if not isinstance(discovery_result, dict):
        return {
            "Status": "DISCOVERY_SELECTION_REJECTED",
            "Reason": "Invalid discovery result.",
            "Selected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    if discovery_result.get("Status") != "MULTI_EXPIRY_DISCOVERY_COMPLETE":
        return {
            "Status": "DISCOVERY_SELECTION_REJECTED",
            "Reason": "Invalid V21.2.23 discovery status.",
            "Selected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    if max_selected < 1:
        return {
            "Status": "DISCOVERY_SELECTION_REJECTED",
            "Reason": "max_selected must be at least 1.",
            "Selected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    developing = discovery_result.get(
        "Developing Candidates",
        [],
    )

    if not isinstance(developing, list):
        developing = []

    valid_candidates: List[Dict[str, Any]] = []

    for candidate in developing:
        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")
        movement = candidate.get("Movement %")
        acceleration = candidate.get("Acceleration")
        state = candidate.get("Discovery State")

        if not symbol:
            continue

        if state != "DEVELOPING":
            continue

        if movement is None or movement <= 0:
            continue

        if acceleration is None or acceleration <= 0:
            continue

        valid_candidates.append(
            {
                **candidate,
                "Selection Status": "SELECTED_FOR_DEEP_OBSERVATION",
                "Deep Observation": "PENDING",
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    valid_candidates.sort(
        key=lambda item: (
            -(item.get("Acceleration") or 0.0),
            -(item.get("Movement %") or 0.0),
            item.get("Trading Symbol", ""),
        )
    )

    selected = valid_candidates[:max_selected]

    rejected_count = len(valid_candidates) - len(selected)

    print()
    print("=" * 70)
    print("V21.2.23.1 DISCOVERY CANDIDATE SELECTION")
    print("=" * 70)
    print(f"Developing Movers Received: {len(developing)}")
    print(f"Valid Developing Movers: {len(valid_candidates)}")
    print(f"Selected For Deep Observation: {len(selected)}")
    print(f"Not Selected: {rejected_count}")
    print()

    if selected:
        print("SELECTED:")
        for rank, candidate in enumerate(selected, start=1):
            print(
                f"{rank:02d}. "
                f"{candidate['Trading Symbol']} | "
                f"{candidate.get('Option Type')} | "
                f"Expiry={candidate.get('Expiry')} | "
                f"Movement={candidate.get('Movement %', 0.0):.2f}% | "
                f"Acceleration={candidate.get('Acceleration', 0.0):.2f}"
            )
    else:
        print("SELECTED: NONE")

    print()
    print("Live Order: False")
    print("Paper Trade: False")

    return {
        "Status": "DISCOVERY_CANDIDATE_SELECTION_COMPLETE",
        "Selected Candidates": selected,
        "Selected Candidate Count": len(selected),
        "Developing Movers Received": len(developing),
        "Valid Developing Movers": len(valid_candidates),
        "Not Selected Count": rejected_count,
        "Selection Limit": max_selected,
        "Selection Rule": (
            "DEVELOPING + positive movement + positive acceleration; "
            "sorted by acceleration, movement, symbol"
        ),
        "Source": "V21.2.23 Multi-Expiry Discovery",
        "Next Stage": "V21.2.19 Deep Observation",
        "Live Order": False,
        "Paper Trade": False,
    }


def _synthetic_test() -> None:
    discovery_result = {
        "Status": "MULTI_EXPIRY_DISCOVERY_COMPLETE",
        "Developing Candidates": [
            {
                "Trading Symbol": "NIFTY26O0623000CE",
                "Option Type": "CE",
                "Expiry": "2026-10-06",
                "Movement %": 5.88,
                "Acceleration": 11.44,
                "Discovery State": "DEVELOPING",
            },
            {
                "Trading Symbol": "NIFTY26O0623150CE",
                "Option Type": "CE",
                "Expiry": "2026-10-06",
                "Movement %": 12.50,
                "Acceleration": 23.61,
                "Discovery State": "DEVELOPING",
            },
            {
                "Trading Symbol": "NIFTY26O1322550PE",
                "Option Type": "PE",
                "Expiry": "2026-10-13",
                "Movement %": 0.78,
                "Acceleration": 1.75,
                "Discovery State": "DEVELOPING",
            },
            {
                "Trading Symbol": "NIFTY26O0622800CE",
                "Option Type": "CE",
                "Expiry": "2026-10-06",
                "Movement %": 5.85,
                "Acceleration": 0.00,
                "Discovery State": "MOVING",
            },
        ],
    }

    result = select_discovery_candidates(
        discovery_result,
        max_selected=3,
    )

    assert result["Status"] == (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    )

    assert result["Selected Candidate Count"] == 3

    selected_symbols = [
        item["Trading Symbol"]
        for item in result["Selected Candidates"]
    ]

    assert selected_symbols[0] == "NIFTY26O0623150CE"
    assert "NIFTY26O0622800CE" not in selected_symbols

    assert result["Live Order"] is False
    assert result["Paper Trade"] is False

    print()
    print(
        "V21.2.23.1 SYNTHETIC TEST: PASS"
    )


if __name__ == "__main__":
    _synthetic_test()
