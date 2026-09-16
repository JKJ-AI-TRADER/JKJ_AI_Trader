"""
JKJ AI Trader
Test — Intraday Option Momentum Adapter V4
"""

import pandas as pd

from modules.intraday_option_momentum_adapter import (
    prepare_option_momentum_data
)


print("=" * 48)
print("JKJ OPTION MOMENTUM ADAPTER V4 TEST")
print("=" * 48)


# ---------------------------------------------------------
# TEST DATA
# ---------------------------------------------------------

rows = []

for i in range(25):
    rows.append(
        {
            "Open": 100 + i,
            "High": 102 + i,
            "Low": 99 + i,
            "Close": 101 + i,
            "Volume": 100000 + (i * 5000),
        }
    )

valid_history = pd.DataFrame(rows)


# ---------------------------------------------------------
# TEST 1 — VALID OPTION HISTORY
# ---------------------------------------------------------

print()
print("TEST 1 — VALID OPTION HISTORY")
print("-" * 48)

result = prepare_option_momentum_data(
    valid_history
)

print("Status:", result["Status"])
print("Data Status:", result["Data Status"])
print("Bars:", result["Bars"])
print("Columns:", result["Columns"])

assert result["Status"] == "READY"
assert result["Data Status"] == "VALID"
assert result["Bars"] == 25

print("PASS")


# ---------------------------------------------------------
# TEST 2 — DATA STRUCTURE
# ---------------------------------------------------------

print()
print("TEST 2 — DATA STRUCTURE")
print("-" * 48)

momentum_data = result["Momentum Data"]

print(momentum_data.head())

assert isinstance(momentum_data, pd.DataFrame)

assert list(momentum_data.columns) == [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

assert len(momentum_data) == 25

print("PASS")


# ---------------------------------------------------------
# TEST 3 — NUMERIC CONVERSION
# ---------------------------------------------------------

print()
print("TEST 3 — NUMERIC CONVERSION")
print("-" * 48)

text_history = valid_history.copy()

text_history["Open"] = text_history["Open"].astype(str)
text_history["High"] = text_history["High"].astype(str)
text_history["Low"] = text_history["Low"].astype(str)
text_history["Close"] = text_history["Close"].astype(str)
text_history["Volume"] = text_history["Volume"].astype(str)

result = prepare_option_momentum_data(
    text_history
)

print("Status:", result["Status"])

assert result["Status"] == "READY"

assert pd.api.types.is_numeric_dtype(
    result["Momentum Data"]["Close"]
)

assert pd.api.types.is_numeric_dtype(
    result["Momentum Data"]["Volume"]
)

print("PASS")


# ---------------------------------------------------------
# TEST 4 — INSUFFICIENT DATA
# ---------------------------------------------------------

print()
print("TEST 4 — INSUFFICIENT DATA")
print("-" * 48)

short_history = valid_history.head(10)

result = prepare_option_momentum_data(
    short_history
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — MISSING COLUMN
# ---------------------------------------------------------

print()
print("TEST 5 — MISSING COLUMN")
print("-" * 48)

missing_history = valid_history.drop(
    columns=["Volume"]
)

result = prepare_option_momentum_data(
    missing_history
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — INVALID CLOSE PRICE
# ---------------------------------------------------------

print()
print("TEST 6 — INVALID CLOSE PRICE")
print("-" * 48)

invalid_price_history = valid_history.copy()

invalid_price_history.loc[
    0,
    "Close"
] = 0

result = prepare_option_momentum_data(
    invalid_price_history
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 7 — NEGATIVE VOLUME
# ---------------------------------------------------------

print()
print("TEST 7 — NEGATIVE VOLUME")
print("-" * 48)

invalid_volume_history = valid_history.copy()

invalid_volume_history.loc[
    0,
    "Volume"
] = -100

result = prepare_option_momentum_data(
    invalid_volume_history
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INVALID INPUT TYPE
# ---------------------------------------------------------

print()
print("TEST 8 — INVALID INPUT TYPE")
print("-" * 48)

result = prepare_option_momentum_data(
    "INVALID"
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 48)
print("JKJ OPTION MOMENTUM ADAPTER V4 TEST COMPLETE")
print("=" * 48)