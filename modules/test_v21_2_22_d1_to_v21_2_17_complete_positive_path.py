"""
JKJ AI Trader

V21.2.22-D.1 → B.1 → V21.2.16 → V21.2.17
Complete Positive-Path Integration Test

Purpose:
    Prove that a candidate explicitly authorized by D.1 is the ONLY
    candidate permitted through the existing B.1 restriction, into the
    existing V21.2.16 decision/entry pipeline, and finally into the
    existing V21.2.17 risk / stop / target evaluation.

Safety:
    - Synthetic data only
    - No Zerodha market data
    - No live orders
    - No paper trades
    - No BUY/SELL
    - No position sizing execution
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

from modules.nifty_option_v21_2_17_risk_stop_targets import (
    evaluate_real_market_risk_stop_targets,
)


LIVE_ORDER = False
PAPER_TRADE = False


print("=" * 72)
print(
    "V21.2.22-D.1 → B.1 → V21.2.16 → V21.2.17 "
    "COMPLETE POSITIVE-PATH TEST"
)
print("=" * 72)
print("Safety: Live Order=False")
print("Safety: Paper Trade=False")
print()


# ---------------------------------------------------------
# 1. Synthetic B.1 qualification
# ---------------------------------------------------------

symbol = "NIFTY26O0622900CE"

b1_result = {
    "Status": "CANDIDATE_QUALIFICATION_COMPLETE",

    "Candidates": {},

    "Qualified Candidates": [
        {
            "Trading Symbol": symbol,
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

    "Selection Source": (
        "V21.2.22-B.1 Candidate Selection"
    ),

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
            "Trading Symbol": symbol,
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
        {
            "Trading Symbol": "NIFTY26O0622850CE",
        },
        {
            "Trading Symbol": "NIFTY26O0622800CE",
        },
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
) == symbol

print("D.1 Authorization: PASS")
print("Authorized Symbol:", symbol)
print()


# ---------------------------------------------------------
# 4. Existing B.1 → V21.2.16 restriction
# ---------------------------------------------------------

selection_for_adapter = {
    "Status": "CANDIDATE_SELECTION_COMPLETE",

    "Selected Candidates": authorized_candidates,

    "Selection Source": (
        "V21.2.22-D.1 Authorization"
    ),

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

print("B.1 → V21.2.16 Restriction: PASS")
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
# Four sequential observations.
# This is converted by the EXISTING adapter into the
# V21.2.15-compatible unified observation.
# ---------------------------------------------------------

observation_store = {
    symbol: [
        {
            "Status": "RECORDED",
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Current Price": 100.00,
            "NIFTY Spot Price": 22600.0,
            "Volume": 100000,
            "Open Interest": 50000,
            "Timestamp": "2026-10-06T09:15:00+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Status": "RECORDED",
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Current Price": 101.00,
            "NIFTY Spot Price": 22602.0,
            "Volume": 120000,
            "Open Interest": 51000,
            "Timestamp": "2026-10-06T09:15:15+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Status": "RECORDED",
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Current Price": 102.50,
            "NIFTY Spot Price": 22605.0,
            "Volume": 145000,
            "Open Interest": 52500,
            "Timestamp": "2026-10-06T09:15:30+05:30",
            "9:15 Price": 100.00,
            "Baseline Source": "GENUINE_915",
            "Live Order": False,
            "Paper Trade": False,
        },
        {
            "Status": "RECORDED",
            "Trading Symbol": symbol,
            "Underlying": "NIFTY",
            "Expiry": "2026-10-06",
            "Strike": 22900,
            "Option Type": "CE",
            "Previous Close": 100.0,
            "Current Price": 104.00,
            "NIFTY Spot Price": 22610.0,
            "Volume": 175000,
            "Open Interest": 54500,
            "Timestamp": "2026-10-06T09:15:45+05:30",
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

assert unified_observation.get("Status") == (
    "UNIFIED_OBSERVATION_COMPLETE"
)

assert unified_observation.get(
    "Observation Count"
) == 4

assert unified_observation.get(
    "Contract Count"
) == 1

print("V21.2.20 → V21.2.16 Adapter: PASS")
print(
    "Unified Observation Count:",
    unified_observation.get("Observation Count"),
)
print(
    "Unified Contract Count:",
    unified_observation.get("Contract Count"),
)
print()


# ---------------------------------------------------------
# 7. Actual V21.2.16 decision/entry pipeline
#
# IMPORTANT:
# Do not construct a synthetic decision result here.
# Use the actual V21.2.16 function.
# ---------------------------------------------------------

decision_result = evaluate_unified_decision_entry(
    unified_observation
)

assert decision_result.get("Status") == (
    "DECISION_ENTRY_COMPLETE"
)

assert decision_result.get("Live Order") is False
assert decision_result.get("Paper Trade") is False

decision_results = decision_result.get(
    "Results",
    [],
)

assert len(decision_results) == 1

print("\n--- ACTUAL V21.2.16 DECISION RESULT ---")
from pprint import pprint
pprint(decision_result)
print("--- END ACTUAL DECISION RESULT ---\n")

assert decision_results[0].get(
    "Trading Symbol"
) == symbol

print("V21.2.16 Decision Entry: PASS")
print(
    "Decision Status:",
    decision_result.get("Status"),
)
print(
    "Decision Candidate Count:",
    len(decision_results),
)
print(
    "Decision Symbol:",
    decision_results[0].get(
        "Trading Symbol"
    ),
)
print()


# ---------------------------------------------------------
# 8. Actual V21.2.17 risk / stop / target pipeline
#
# IMPORTANT:
# The SAME unified observation is passed through.
# No new market observations are created.
# ---------------------------------------------------------

risk_result = evaluate_real_market_risk_stop_targets(
    decision_result,
    unified_observation,
)

assert risk_result.get("Status") == (
    "RISK_STOP_TARGETS_COMPLETE"
)

assert risk_result.get("Live Order") is False
assert risk_result.get("Paper Trade") is False

risk_results = risk_result.get(
    "Results",
    [],
)

assert len(risk_results) == 1

risk_item = risk_results[0]

assert risk_item.get(
    "Trading Symbol"
) == symbol

assert risk_item.get(
    "Entry Qualification"
) == "ENTRY_QUALIFIED"

assert risk_item.get(
    "Stop Price"
) is not None

assert risk_item.get(
    "Target 1"
) is not None

assert risk_item.get(
    "Target 2"
) is not None

assert risk_item.get(
    "Target 3"
) is not None

print("V21.2.17 Risk / Stop / Targets: PASS")
print(
    "Risk Status:",
    risk_result.get("Status"),
)
print(
    "Risk Symbol:",
    risk_item.get("Trading Symbol"),
)
print(
    "Entry Qualification:",
    risk_item.get("Entry Qualification"),
)
print(
    "Entry Risk Context:",
    risk_item.get("Entry Risk Context"),
)
print(
    "Stop Price:",
    risk_item.get("Stop Price"),
)
print(
    "Target 1:",
    risk_item.get("Target 1"),
)
print(
    "Target 2:",
    risk_item.get("Target 2"),
)
print(
    "Target 3:",
    risk_item.get("Target 3"),
)
print()


# ---------------------------------------------------------
# 9. Final safety assertions
# ---------------------------------------------------------

assert risk_result.get("Live Order") is False
assert risk_result.get("Paper Trade") is False

assert risk_item.get(
    "Trading Symbol"
) == symbol

assert risk_item.get(
    "Entry Qualification"
) == "ENTRY_QUALIFIED"


# ---------------------------------------------------------
# 10. Final result
# ---------------------------------------------------------

print("=" * 72)
print(
    "V21.2.22-D.1 → B.1 → V21.2.16 → V21.2.17 "
    "COMPLETE POSITIVE-PATH TEST PASS"
)
print("=" * 72)
print("D.1 Authorization:          PASS")
print("B.1 Restriction:            PASS")
print("Unified Observation:        PASS")
print("V21.2.16 Decision Entry:    PASS")
print("V21.2.17 Risk Evaluation:   PASS")
print("Stop / Targets Generated:   PASS")
print("Authorized Candidate Count: 1")
print("Final Risk Candidate Count: 1")
print("Final Symbol:", symbol)
print("Live Order:                 False")
print("Paper Trade:                False")
print("BUY/SELL:                   NOT EXECUTED")
print("=" * 72)