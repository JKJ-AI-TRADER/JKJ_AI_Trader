"""
JKJ AI TRADER
V21.2.18 - Daily 9:15 Baseline Store

Purpose:
    Persist the genuine market-open baseline for the trading day.

Rules:
    - A baseline belongs to one trading date.
    - The baseline timestamp is recorded.
    - A later snapshot must never be silently treated as 9:15 data.
    - No trading decisions.
    - No live orders.
    - No paper trades.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


BASELINE_FILE = Path(".jkj_v21_2_18_915_baseline.json")


def save_baseline(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a successfully captured baseline.

    The result must explicitly identify itself as a completed
    baseline capture.
    """

    if result.get("Status") != "BASELINE_CAPTURE_COMPLETE":
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "Invalid baseline capture result",
        }

    if result.get("Baseline Type") != "GENUINE_915":
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "Baseline is not marked GENUINE_915",
        }

    captured_at = str(result.get("Captured At", ""))

    if not captured_at or captured_at == "TEST_ONLY":
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "Invalid capture timestamp",
        }

    if result.get("Baseline Count", 0) <= 0:
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "No baseline records captured",
        }

    payload = {
        "Trading Date": datetime.now().date().isoformat(),
        "Baseline Type": result.get("Baseline Type", "UNKNOWN"),
        "Baseline": result,
    }

    BASELINE_FILE.write_text(
        json.dumps(
            payload,
            indent=2,
            default=str,
        )
    )

    return {
        "Status": "BASELINE_SAVED",
        "Trading Date": payload["Trading Date"],
        "File": str(BASELINE_FILE),
    }


def load_today_baseline() -> Optional[Dict[str, Any]]:
    """
    Load today's stored baseline.

    Returns None if:
        - no baseline exists
        - file is invalid
        - baseline belongs to another trading date
    """

    if not BASELINE_FILE.exists():
        return None

    try:
        payload = json.loads(
            BASELINE_FILE.read_text()
        )
    except Exception:
        return None

    today = datetime.now().date().isoformat()

    if payload.get("Trading Date") != today:
        return None

    baseline = payload.get("Baseline")

    if not baseline:
        return None

    # Never allow a test/synthetic baseline to be used
    # as the genuine market-open baseline.
    if payload.get("Baseline Type") != "GENUINE_915":
        return None

    return baseline


def baseline_available_today() -> bool:
    return load_today_baseline() is not None
