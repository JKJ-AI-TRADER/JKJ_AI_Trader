"""
JKJ AI Trader
Test — Intraday Option Contract Mapper V2
"""

from intraday_option_contract_mapper import (
    map_nifty_option_contracts
)


print("=" * 41)
print("JKJ OPTION CONTRACT MAPPER V2 TEST")
print("=" * 41)


# ---------------------------------------------------------
# TEST DATA
# ---------------------------------------------------------

candidates = [
    {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23200,
        "Option Type": "CE",
        "Distance From ATM": -100,
    },
    {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23200,
        "Option Type": "PE",
        "Distance From ATM": -100,
    },
    {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23300,
        "Option Type": "CE",
        "Distance From ATM": 0,
    },
    {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23300,
        "Option Type": "PE",
        "Distance From ATM": 0,
    },
]


instrument_records = [
    {
        "name": "NIFTY",
        "expiry": "2026-09-15",
        "strike": 23200,
        "instrument_type": "CE",
        "tradingsymbol": "NIFTY15SEP2623200CE",
        "instrument_token": 111111,
        "lot_size": 75,
        "exchange": "NFO",
    },
    {
        "name": "NIFTY",
        "expiry": "2026-09-15",
        "strike": 23200,
        "instrument_type": "PE",
        "tradingsymbol": "NIFTY15SEP2623200PE",
        "instrument_token": 111112,
        "lot_size": 75,
        "exchange": "NFO",
    },
    {
        "name": "NIFTY",
        "expiry": "2026-09-15",
        "strike": 23300,
        "instrument_type": "CE",
        "tradingsymbol": "NIFTY15SEP2623300CE",
        "instrument_token": 111113,
        "lot_size": 75,
        "exchange": "NFO",
    },
    {
        "name": "NIFTY",
        "expiry": "2026-09-15",
        "strike": 23300,
        "instrument_type": "PE",
        "tradingsymbol": "NIFTY15SEP2623300PE",
        "instrument_token": 111114,
        "lot_size": 75,
        "exchange": "NFO",
    },
]


# ---------------------------------------------------------
# TEST 1 — FULL MATCH
# ---------------------------------------------------------

print()
print("TEST 1 — FULL CONTRACT MATCH")
print("-" * 41)

result = map_nifty_option_contracts(
    candidates,
    instrument_records
)

print("Status:", result["Status"])
print("Matched Count:", result["Matched Count"])
print("Unmatched Count:", result["Unmatched Count"])

assert result["Status"] == "READY"
assert result["Matched Count"] == 4
assert result["Unmatched Count"] == 0

print("PASS")


# ---------------------------------------------------------
# TEST 2 — CONTRACT DETAILS
# ---------------------------------------------------------

print()
print("TEST 2 — CONTRACT DETAILS")
print("-" * 41)

for contract in result["Matched Contracts"]:
    print(contract)

    assert contract["Underlying"] == "NIFTY"
    assert contract["Exchange"] == "NFO"
    assert contract["Lot Size"] == 75
    assert contract["Trading Symbol"]
    assert contract["Instrument Token"]

print("PASS")


# ---------------------------------------------------------
# TEST 3 — PARTIAL MATCH
# ---------------------------------------------------------

print()
print("TEST 3 — PARTIAL MATCH")
print("-" * 41)

partial_records = instrument_records[:2]

result = map_nifty_option_contracts(
    candidates,
    partial_records
)

print("Status:", result["Status"])
print("Matched Count:", result["Matched Count"])
print("Unmatched Count:", result["Unmatched Count"])

assert result["Status"] == "PARTIAL MATCH"
assert result["Matched Count"] == 2
assert result["Unmatched Count"] == 2

print("PASS")


# ---------------------------------------------------------
# TEST 4 — NO MATCH
# ---------------------------------------------------------

print()
print("TEST 4 — NO MATCH")
print("-" * 41)

wrong_records = [
    {
        "name": "BANKNIFTY",
        "expiry": "2026-09-15",
        "strike": 52000,
        "instrument_type": "CE",
        "tradingsymbol": "BANKNIFTY15SEP2652000CE",
        "instrument_token": 222222,
        "lot_size": 30,
        "exchange": "NFO",
    }
]

result = map_nifty_option_contracts(
    candidates,
    wrong_records
)

print("Status:", result["Status"])
print("Matched Count:", result["Matched Count"])
print("Unmatched Count:", result["Unmatched Count"])

assert result["Status"] == "NO MATCH"
assert result["Matched Count"] == 0
assert result["Unmatched Count"] == 4

print("PASS")


# ---------------------------------------------------------
# TEST 5 — INVALID INPUT
# ---------------------------------------------------------

print()
print("TEST 5 — INVALID INPUT")
print("-" * 41)

result = map_nifty_option_contracts(
    "INVALID",
    instrument_records
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 41)
print("JKJ OPTION CONTRACT MAPPER V2 TEST COMPLETE")
print("=" * 41)