"""
JKJ AI TRADER
V21.2.18 - Daily 9:15 Baseline Store

Persists only a validated genuine market-open baseline.
No trading decisions, live orders, or paper trades.
"""

from __future__ import annotations

import json
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
BASELINE_FILE = Path(".jkj_v21_2_18_915_baseline.json")
CAPTURE_START = time(9, 14, 30)
CAPTURE_END = time(9, 16, 0)


def _now_ist() -> datetime:
    return datetime.now(IST)


def baseline_file_for_date(
    trading_date: Optional[datetime] = None,
    base_path: Optional[Path] = None,
) -> Path:
    """Return a separate baseline filename for one timezone-aware IST date."""
    target = _now_ist() if trading_date is None else trading_date
    if (
        not isinstance(target, datetime)
        or target.tzinfo is None
        or target.utcoffset() is None
    ):
        raise ValueError("trading_date must be a timezone-aware datetime.")

    date_key = target.astimezone(IST).date().isoformat()
    source = Path(base_path) if base_path is not None else BASELINE_FILE
    return source.with_name(f"{source.stem}_{date_key}{source.suffix}")


def _parse_valid_capture(result: Dict[str, Any]) -> Optional[datetime]:
    if result.get("Status") != "BASELINE_CAPTURE_COMPLETE":
        return None
    if result.get("Baseline Type") != "GENUINE_915":
        return None

    records = result.get("Baseline")
    if not isinstance(records, list) or not records:
        return None
    if result.get("Baseline Count", 0) != len(records):
        return None

    captured_text = result.get("Captured At")
    if not isinstance(captured_text, str) or not captured_text.strip():
        return None

    try:
        captured = datetime.fromisoformat(captured_text)
    except (TypeError, ValueError):
        return None

    if captured.tzinfo is None or captured.utcoffset() is None:
        return None

    captured = captured.astimezone(IST)
    if not CAPTURE_START <= captured.time().replace(tzinfo=None) <= CAPTURE_END:
        return None

    # Every record must carry the same timezone-aware capture timestamp.
    for record in records:
        if not isinstance(record, dict):
            return None
        record_text = record.get("Captured At")
        if not isinstance(record_text, str) or not record_text.strip():
            return None
        try:
            record_time = datetime.fromisoformat(record_text)
        except (TypeError, ValueError):
            return None
        if record_time.tzinfo is None or record_time.utcoffset() is None:
            return None
        if record_time.astimezone(IST) != captured:
            return None

    return captured


def save_baseline(
    result: Dict[str, Any],
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Validate before writing; rejected input never overwrites a file."""
    captured = _parse_valid_capture(result)
    if captured is None:
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": (
                "Capture must be GENUINE_915, timestamped within "
                "09:14:30–09:16:00 IST, and contain matching non-empty records."
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    payload = {
        "Trading Date": captured.date().isoformat(),
        "Baseline Type": "GENUINE_915",
        "Baseline": result,
    }

    # Default writes are date-specific. Explicit paths remain available
    # for controlled offline tests and deliberate file handling.
    destination = (
        Path(path) if path is not None else baseline_file_for_date(captured)
    )
    # Preserve the first saved baseline for this date; never replace it.
    if destination.exists():
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "A baseline file already exists; refusing to overwrite it.",
            "File": str(destination),
            "Live Order": False,
            "Paper Trade": False,
        }

    try:
        with destination.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, default=str)
    except FileExistsError:
        return {
            "Status": "BASELINE_NOT_SAVED",
            "Reason": "A baseline file already exists; refusing to overwrite it.",
            "File": str(destination),
            "Live Order": False,
            "Paper Trade": False,
        }

    return {
        "Status": "BASELINE_SAVED",
        "Trading Date": payload["Trading Date"],
        "File": str(destination),
        "Live Order": False,
        "Paper Trade": False,
    }


def load_today_baseline(
    path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """Load only a valid genuine baseline from today's date-specific IST file."""
    current = now or _now_ist()
    if (
        not isinstance(current, datetime)
        or current.tzinfo is None
        or current.utcoffset() is None
    ):
        return None

    today = current.astimezone(IST).date().isoformat()
    destination = (
        Path(path) if path is not None else baseline_file_for_date(current)
    )
    if not destination.exists():
        return None

    try:
        payload = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    if payload.get("Trading Date") != today:
        return None
    if payload.get("Baseline Type") != "GENUINE_915":
        return None

    baseline = payload.get("Baseline")
    if not isinstance(baseline, dict):
        return None
    if _parse_valid_capture(baseline) is None:
        return None
    if baseline.get("Captured At", "")[:10] != today:
        # Compare the timestamp's actual IST date, not its textual offset date.
        try:
            captured = datetime.fromisoformat(baseline["Captured At"]).astimezone(IST)
        except (TypeError, ValueError):
            return None
        if captured.date().isoformat() != today:
            return None

    return baseline


def baseline_available_today() -> bool:
    return load_today_baseline() is not None
