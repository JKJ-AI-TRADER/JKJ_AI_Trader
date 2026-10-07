"""
JKJ AI Trader

V21.2.22-D.1 → V21.2.16 Decision/Entry Positive-Path Test

Purpose:
    Prove that a candidate authorized by D.1 can pass through the
    existing V21.2.20 → V21.2.16 observation adapter and reach the
    existing V21.2.16 decision/entry pipeline.

Safety:
    - Synthetic observations only
    - No Zerodha market data
    - No live orders
    - No paper trades
    - No BUY/SELL
    - No position sizing
    - No stop/target execution
"""

from modules.nifty_option_v21_2_22_d1_to_b1_authorization import (
    build_d1_authorized_b1_result,
)

from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)

from modules.nifty_option_v21_2_20_to_v21_2_16_adapter import (
    build_unified_observation_from_qualified_candidates,
)

from modules.nifty_option_v21_2_16_decision_entry import (
    evaluate_unified_decision_entry,
)


LIVE_ORDER = False
PAPER_TRADE = False


print("=" * 72)
print("V21.2.22-D.1 → V21.2.16 DECISION/ENTRY PATH TEST")
print("=" * 72)
print("Safety: Live Order=False")
print("Safety: Paper Trade=False")
print()


# ---------------------------------------------------------
# 1. Synthetic B.1 qualification
# ---------------------------------------------------------

b1_result = {
    "Status": "CANDIDATE_QUALIFICATION_COMPLETE",

    "Candidates": {},

    "Qualified Candidates": [
        {
            "Trading Symbol": "NIFTY26O0622900CE",
            "Qualification": "STRONG_DEVELOPING_CANDIDATE",
        },
        {
            "Trading Symbol": "NIFTY26O0622850CE",
            "Qualification": "DEVELOPING_CANDIDATE",
        },
        {
            "Trading Symbol": "NIFTY26O0622800CE",
            "Qualification": "DEVELOPING_CANDIDATE",
        },
    ],

    "Selection Applied": True,
    "Selection Source": "V21.2.22-B.1 Candidate Selection",
    "Original Qualification Source": (
        "V21.2.20 Candidate Qualification"
    ),

    "Live Order": False,
    "Paper Trade": False,
}


# ---------------------------------------------------------
# 2. Synthetic D.1 authorization
#
# Only 2900CE is authorized.
# ---------------------------------------------------------

d1_result = {
    "Status": "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE",

    "Accepted Candidates": [
        {
            "Trading Symbol": "NIFTY26O0622900CE",
            "Lifecycle": "STRENGTHENING",
            "Qualification": "STRONG_DEVELOPING_CANDIDATE",
            "V12.6 Persistence": "PERSISTENT",
            "V12.6 Direction": "UP",
            "V12.6 Confirmation": "CONFIRMED",
            "Evidence Gate": "PASSED",
            "Entry Evaluation": "PENDING",
            "Live Order": False,
            "Paper Trade": False,
        }
    ],

    "Rejected Candidates": [
        {"Trading Symbol": "NIFTY26O0622850CE"},
        {"Trading Symbol": "NIFTY26O0622800CE"},
    ],

    "Accepted Candidate Count": 1,
    "Rejected Candidate Count": 2,
    "Next Stage": "EXISTING_ENTRY_QUALIFICATION",

    "Live Order": False,
    "Paper Trade": False,
}


# ---------------------------------------------------------
# 3. D.1 → B.1 authorization
# ---------------------------------------------------------

authorized_result = build_d1_authorized_b1_result(
    b1_result,
    d1_result,
)

assert authorized_result.get("Status") == (
    "D1_AUTHORIZED_B1_RESULT_COMPLETE"
)

assert authorized_result.get(
    "Authorized Candidate Count"
) == 1

authorized_candidates = authorized_result.get(
    "Qualified Candidates",
    [],
)

assert len(authorized_candidates) == 1
assert authorized_candidates[0].get(
    "Trading Symbol"
) == "NIFTY26O0622900CE"

print("D.1 Authorization:", "PASS")
print(
    "Authorized Symbol:",
    authorized_candidates[0].get("Trading Symbol"),
)
print()


# ---------------------------------------------------------
# 4. Existing B.1 → V21.2.16 restriction
# ---------------------------------------------------------

selection_for_adapter = {
    "Status": "CANDIDATE_SELECTION_COMPLETE",
    "Selected Candidates": authorized_candidates,
    "Selection Source": "V21.2.22-D.1 Authorization",
    "Live Order": False,
    "Paper Trade": False,
}

selected_qualification = build_selected_qualification_result(
    b1_result,
    selection_for_adapter,
)

assert selected_qualification.get("Status") == (
    "CANDIDATE_QUALIFICATION_COMPLETE"
)

assert selected_qualification.get(
    "Qualified Candidate Count"
) == 1

print("B.1 → V21.2.16 Restriction:", "PASS")
print(
    "Restricted Candidate Count:",
    selected_qualification.get(
        "Qualified Candidate Count"
    ),
)
print()


# ---------------------------------------------------------
# 5. Synthetic V21.2.19 observation store
#
# Four observations are supplied so the existing adapter
# can construct the V21.2.15-compatible unified observation.
# ---------------------------------------------------------

symbol = "NIFTY26O0622900CE"

observation_store = {
    symbol: [
        {
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Latest Price": 100.00,
            "Observation Timestamp": "2026-10-06T09:15:00+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Latest Price": 101.00,
            "Observation Timestamp": "2026-10-06T09:15:15+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Latest Price": 102.50,
            "Observation Timestamp": "2026-10-06T09:15:30+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Latest Price": 104.00,
            "Observation Timestamp": "2026-10-06T09:15:45+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
    ]
}


# ---------------------------------------------------------
# 6. Existing V21.2.20 → V21.2.16 adapter
# ---------------------------------------------------------

unified_observation = (
    build_unified_observation_from_qualified_candidates(
        observation_store,
        selected_qualification,
    )
)

print(
    "Unified Observation Status:",
    unified_observation.get("Status"),
)

print(
    "Unified Observation Count:",
    unified_observation.get("Observation Count"),
)

print(
    "Unified Contract Count:",
    unified_observation.get("Contract Count"),
)

assert unified_observation.get("Status") == (
    "UNIFIED_OBSERVATION_COMPLETE"
)

assert unified_observation.get(
    "Observation Count"
) == 4

assert unified_observation.get(
    "Contract Count"
) == 1

print("V21.2.20 → V21.2.16 Adapter:", "PASS")
print()


# ---------------------------------------------------------
# 7. Actual V21.2.16 decision/entry pipeline
# ---------------------------------------------------------

decision_result = evaluate_unified_decision_entry(
    unified_observation
)

print(
    "V21.2.16 Decision Status:",
    decision_result.get("Status"),
)

print(
    "Decision Result Keys:",
    list(decision_result.keys()),
)

print(
    "Live Order:",
    decision_result.get("Live Order"),
)

print(
    "Paper Trade:",
    decision_result.get("Paper Trade"),
)

print()


# ---------------------------------------------------------
# 8. Safety assertions
# ---------------------------------------------------------

assert decision_result.get("Live Order") is False
assert decision_result.get("Paper Trade") is False

assert decision_result.get("Status") == (
    "DECISION_ENTRY_COMPLETE"
)

print("=" * 72)
print("V21.2.22-D.1 → V21.2.16 DECISION PATH TEST PASS")
print("=" * 72)
print("D.1 Authorization:        PASS")
print("B.1 Restriction:          PASS")
print("Unified Observation:      PASS")
print("V21.2.16 Decision Entry:  PASS")
print("Live Order:               False")
print("Paper Trade:              False")
print("BUY/SELL:                 NOT EXECUTED")
print("=" * 72)
