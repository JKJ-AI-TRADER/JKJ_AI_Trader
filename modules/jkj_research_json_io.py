"""Safe JSON writing utilities for JKJ research artifacts."""

import json
import os
from datetime import date, datetime
from pathlib import Path


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )


def write_json_new(path, data):
    """Atomically create a new JSON file without overwriting existing files."""
    target = Path(path)
    temporary = target.with_name(target.name + ".tmp")

    # Serialize first; errors here create or modify no files.
    payload = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    ) + "\n"

    if target.exists():
        raise FileExistsError(f"Refusing to overwrite: {target}")
    if temporary.exists():
        raise FileExistsError(f"Temporary file already exists: {temporary}")

    created_temp = False
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            created_temp = True
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        # Create the final name atomically, without replacing an existing file.
        os.link(temporary, target)
    finally:
        if created_temp and temporary.exists():
            temporary.unlink()

    return target
