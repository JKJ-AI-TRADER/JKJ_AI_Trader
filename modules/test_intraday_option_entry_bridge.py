"""
JKJ AI Trader
Test — Intraday Option Entry Bridge V8
"""

from modules.intraday_option_entry_bridge import (
    evaluate_option_entry
)


print("=" * 55)
print("JKJ OPTION ENTRY BRIDGE V8 TEST")
print("=" * 55)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def strong_momentum(
    score=90,
    exhaustion=0
):
    return {
        "Status": "READY",
        "Momentum Score": score,
        "Momentum Status": "STRONG MOMENTUM",
        "Trade Candidate": True,
        "Exhaustion Penalty": exhaustion,
    }


def strong_opportunity():
    return {
        "Status": "READY",
        "Decision": "STRONG ENTRY CANDIDATE",
        "Confidence": 90,
    }


def normal_opportunity():
    return {
        "Status": "READY",
        "Decision": "ENTRY CANDIDATE",
        "Confidence": 85,
    }


# ---------------------------------------------------------
# TEST 1 — STRONG OPTION ENTRY
# ---------------------------------------------------------

print()
print("TEST 1 — STRONG OPTION ENTRY")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(
        score=90,
        exhaustion=0
    ),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=112.50,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Risk Amount:", result["Risk Amount"])
print("Reward Amount:", result["Reward Amount"])
print("Risk Reward Ratio:", result["Risk Reward Ratio"])
print("Momentum Score:", result["Momentum Score"])

assert result["Status"] == "READY"
assert result["Decision"] == "STRONG ENTRY CANDIDATE"
assert result["Risk Amount"] == 5.0
assert result["Reward Amount"] == 12.5
assert result["Risk Reward Ratio"] == 2.5
assert result["Momentum Score"] == 90

print("PASS")


# ---------------------------------------------------------
# TEST 2 — NORMAL OPTION ENTRY
# ---------------------------------------------------------

print()
print("TEST 2 — NORMAL OPTION ENTRY")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=normal_opportunity(),
    momentum_result=strong_momentum(
        score=82,
        exhaustion=0
    ),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=110.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Risk Reward Ratio:", result["Risk Reward Ratio"])

assert result["Status"] == "READY"
assert result["Decision"] == "ENTRY CANDIDATE"
assert result["Risk Reward Ratio"] == 2.0

print("PASS")


# ---------------------------------------------------------
# TEST 3 — SEVERE EXHAUSTION
# ---------------------------------------------------------

print()
print("TEST 3 — SEVERE EXHAUSTION")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(
        score=95,
        exhaustion=-13
    ),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=115.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 4 — OPTION AGAINST UNDERLYING
# ---------------------------------------------------------

print()
print("TEST 4 — OPPORTUNITY MUST ALREADY BE VALID")
print("-" * 55)

bad_opportunity = {
    "Status": "READY",
    "Decision": "NO TRADE",
    "Confidence": 100,
}

result = evaluate_option_entry(
    opportunity_result=bad_opportunity,
    momentum_result=strong_momentum(
        score=90,
        exhaustion=0
    ),
    option_type="PE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=112.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — LOW RISK/REWARD
# ---------------------------------------------------------

print()
print("TEST 5 — LOW RISK/REWARD")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(
        score=90,
        exhaustion=0
    ),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=106.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Risk Reward Ratio:", result["Risk Reward Ratio"])

assert result["Status"] == "READY"
assert result["Decision"] == "NO TRADE"
assert result["Risk Reward Ratio"] == 1.2

print("PASS")


# ---------------------------------------------------------
# TEST 6 — INVALID OPTION TYPE
# ---------------------------------------------------------

print()
print("TEST 6 — INVALID OPTION TYPE")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(),
    option_type="XX",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=110.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 7 — INVALID STOP LOSS
# ---------------------------------------------------------

print()
print("TEST 7 — INVALID STOP LOSS")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=105.00,
    target_price=115.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 8 — INVALID QUANTITY
# ---------------------------------------------------------

print()
print("TEST 8 — INVALID QUANTITY")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result=strong_momentum(),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=110.00,
    quantity=0,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 9 — INVALID OPPORTUNITY INPUT
# ---------------------------------------------------------

print()
print("TEST 9 — INVALID OPPORTUNITY INPUT")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result="INVALID",
    momentum_result=strong_momentum(),
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=110.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 10 — INVALID MOMENTUM INPUT
# ---------------------------------------------------------

print()
print("TEST 10 — INVALID MOMENTUM INPUT")
print("-" * 55)

result = evaluate_option_entry(
    opportunity_result=strong_opportunity(),
    momentum_result="INVALID",
    option_type="CE",
    entry_price=100.00,
    stop_loss_price=95.00,
    target_price=110.00,
    quantity=75,
)

print("Status:", result["Status"])
print("Decision:", result["Decision"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 55)
print("JKJ OPTION ENTRY BRIDGE V8 TEST COMPLETE")
print("=" * 55)