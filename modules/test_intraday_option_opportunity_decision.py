"""
JKJ AI Trader
Test — Intraday Option Opportunity Decision V7
"""

from intraday_option_opportunity_decision import (
    decide_option_opportunity
)


print("=" * 55)
print("JKJ OPTION OPPORTUNITY DECISION V7 TEST")
print("=" * 55)


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def momentum(
    score=90,
    candidate=True,
    exhaustion=0,
    status="STRONG MOMENTUM",
):
    return {
        "Status": "READY",
        "Momentum Score": score,
        "Momentum Status": status,
        "Trade Candidate": candidate,
        "Exhaustion Score": exhaustion,
    }


def enrichment(
    alignment="SUPPORTIVE",
    liquidity="EXCELLENT",
    economics="VIABLE",
    underlying_momentum="HEALTHY",
):
    return {
        "Status": "READY",
        "Option Alignment": alignment,
        "Liquidity Status": liquidity,
        "Economic Status": economics,
        "Underlying Momentum": underlying_momentum,
    }


# ---------------------------------------------------------
# TEST 1 — STRONG ENTRY CANDIDATE
# ---------------------------------------------------------

print()
print("TEST 1 — STRONG ENTRY CANDIDATE")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=90,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="EXCELLENT",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])

assert result["Status"] == "READY"
assert result["Decision"] == "STRONG ENTRY CANDIDATE"
assert result["Confidence"] == 90

print("PASS")


# ---------------------------------------------------------
# TEST 2 — NORMAL ENTRY CANDIDATE
# ---------------------------------------------------------

print()
print("TEST 2 — ENTRY CANDIDATE")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=82,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="GOOD",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])

assert result["Status"] == "READY"
assert result["Decision"] == "ENTRY CANDIDATE"
assert result["Confidence"] == 85

print("PASS")


# ---------------------------------------------------------
# TEST 3 — EXHAUSTION CAUTION
# ---------------------------------------------------------

print()
print("TEST 3 — EXHAUSTION CAUTION")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=88,
        candidate=True,
        exhaustion=-11,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="GOOD",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "ENTRY CANDIDATE"
assert result["Confidence"] == 80

print("PASS")


# ---------------------------------------------------------
# TEST 4 — SEVERE EXHAUSTION
# ---------------------------------------------------------

print()
print("TEST 4 — SEVERE EXHAUSTION")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=95,
        candidate=True,
        exhaustion=-13,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="EXCELLENT",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert result["Confidence"] == 100

print("PASS")


# ---------------------------------------------------------
# TEST 5 — AGAINST UNDERLYING
# ---------------------------------------------------------

print()
print("TEST 5 — OPTION AGAINST UNDERLYING")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=92,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="AGAINST",
        liquidity="EXCELLENT",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert result["Confidence"] == 90

print("PASS")


# ---------------------------------------------------------
# TEST 6 — POOR LIQUIDITY
# ---------------------------------------------------------

print()
print("TEST 6 — POOR LIQUIDITY")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=92,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="POOR",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert result["Confidence"] == 100

print("PASS")


# ---------------------------------------------------------
# TEST 7 — NON-VIABLE ECONOMICS
# ---------------------------------------------------------

print()
print("TEST 7 — NON-VIABLE ECONOMICS")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=92,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="EXCELLENT",
        economics="NOT VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert result["Confidence"] == 100

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INFORMATION PENDING
# ---------------------------------------------------------

print()
print("TEST 8 — INFORMATION PENDING")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=90,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="PENDING",
        economics="PENDING",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "WATCH"
assert result["Confidence"] == 70

print("PASS")


# ---------------------------------------------------------
# TEST 9 — MOMENTUM BELOW THRESHOLD
# ---------------------------------------------------------

print()
print("TEST 9 — LOW MOMENTUM")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=65,
        candidate=False,
        exhaustion=0,
        status="DEVELOPING",
    ),
    enrichment(
        alignment="SUPPORTIVE",
        liquidity="EXCELLENT",
        economics="VIABLE",
        underlying_momentum="HEALTHY",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 10 — MIXED / CAUTIOUS
# ---------------------------------------------------------

print()
print("TEST 10 — MIXED CONFIRMATION")
print("-" * 55)

result = decide_option_opportunity(
    momentum(
        score=84,
        candidate=True,
        exhaustion=0,
    ),
    enrichment(
        alignment="MIXED",
        liquidity="ACCEPTABLE",
        economics="VIABLE",
        underlying_momentum="WEAK",
    ),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Confidence:", result["Confidence"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "READY"
assert result["Decision"] == "WATCH"
assert result["Confidence"] == 65

print("PASS")


# ---------------------------------------------------------
# TEST 11 — INVALID MOMENTUM INPUT
# ---------------------------------------------------------

print()
print("TEST 11 — INVALID MOMENTUM INPUT")
print("-" * 55)

result = decide_option_opportunity(
    "INVALID",
    enrichment(),
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 12 — INVALID ENRICHMENT INPUT
# ---------------------------------------------------------

print()
print("TEST 12 — INVALID ENRICHMENT INPUT")
print("-" * 55)

result = decide_option_opportunity(
    momentum(),
    "INVALID",
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 55)
print("JKJ OPTION OPPORTUNITY DECISION V7 TEST COMPLETE")
print("=" * 55)