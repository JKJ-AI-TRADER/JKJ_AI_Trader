"""
JKJ AI Trader
V21.2.22-D.1 — Real-Market D → D.1 Regression Test

Purpose:
    Validate the final evidence gate and evidence-gated entry bridge
    using the existing real-market evidence/reconciliation pipeline.

Safety:
    No live orders.
    No paper trades.
    No BUY/SELL.
    No position sizing.
    No stop/target execution.
"""

from modules.jkj_daily_zerodha_auth import authenticate_today
from modules.nifty_option_v21_2_19_persistent_observer import (
    run_persistent_observer,
)
from modules.nifty_option_v21_2_20_candidate_qualification import (
    qualify_candidates,
)
from modules.nifty_option_v21_2_22_b_candidate_refresh_v2 import (
    refresh_developing_candidates_v2,
)
from modules.nifty_option_v21_2_22_b1_candidate_selection import (
    select_candidates,
)
from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    collect_detailed_evidence,
)
from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)
from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)
from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)
from modules.nifty_option_v21_2_22_d_final_evidence_gate import (
    evaluate_final_evidence_gate,
)
from modules.nifty_option_v21_2_22_d1_entry_bridge import (
    build_entry_bridge,
)
from modules.nifty_option_v21_2_22_d1_to_b1_authorization import (
    build_d1_authorized_b1_result,
)


LIVE_ORDER = False
PAPER_TRADE = False


print("=" * 70)
print("V21.2.22-D.1 REAL-MARKET REGRESSION TEST")
print("=" * 70)
print("Safety: Live Order=False")
print("Safety: Paper Trade=False")
print()

# ---------------------------------------------------------
# 1. Zerodha authentication
# ---------------------------------------------------------
auth_result = authenticate_today()

if auth_result.get("Kite") is None:
    raise RuntimeError("Zerodha session unavailable.")

kite = auth_result["Kite"]

print("Zerodha:", auth_result.get("Status"))
print("Session ready: YES")
print()

# ---------------------------------------------------------
# 2. V21.2.19 persistent observation
# ---------------------------------------------------------
observer_result = run_persistent_observer(
    kite=kite,
    interval_seconds=15,
    max_observations=4,
    strikes_each_side=10,
)

print("Observer Status:", observer_result.get("Status"))
print(
    "Observation Count:",
    observer_result.get("Observation Count"),
)
print(
    "Universe Count:",
    observer_result.get("Universe Count"),
)
print()

# ---------------------------------------------------------
# 3. V21.2.20 qualification
# ---------------------------------------------------------
lifecycle_store = observer_result.get(
    "Candidate Lifecycle",
    {},
)

qualification_result = qualify_candidates(
    lifecycle_store
)

print(
    "Qualification Status:",
    qualification_result.get("Status")
)
print(
    "Qualified Candidates:",
    len(
        qualification_result.get(
            "Qualified Candidates",
            [],
        )
    ),
)
print()

# ---------------------------------------------------------
# 4. B v2 candidate refresh
# ---------------------------------------------------------
refresh_result = refresh_developing_candidates_v2(
    lifecycle_store
)

print(
    "B v2 Status:",
    refresh_result.get("Status")
)
print(
    "Developing Candidates:",
    len(
        refresh_result.get(
            "Developing Candidates",
            [],
        )
    ),
)
print()

# ---------------------------------------------------------
# 5. B.1 candidate selection
# ---------------------------------------------------------
selection_result = select_candidates(
    refresh_result
)

print(
    "B.1 Status:",
    selection_result.get("Status")
)

selected_candidates = selection_result.get(
    "Selected Candidates",
    [],
)

print(
    "Selected Candidates:",
    len(selected_candidates)
)

for candidate in selected_candidates:
    print(
        "  -",
        candidate.get("Trading Symbol"),
        candidate.get("Category"),
    )

print()

# ---------------------------------------------------------
# 6. B.1 → V21.2.16 adapter
# ---------------------------------------------------------
selected_qualification = (
    build_selected_qualification_result(
        qualification_result,
        selection_result,
    )
)

# ---------------------------------------------------------
# 7. B.2 detailed evidence
# ---------------------------------------------------------
detailed_evidence = collect_detailed_evidence(
    kite=kite,
    selection_result=selection_result,
    observation_count=4,
    interval_seconds=15,
)

print(
    "B.2 Status:",
    detailed_evidence.get("Status")
)
print(
    "Detailed Evidence Candidates:",
    len(
        detailed_evidence.get(
            "Results",
            [],
        )
    ),
)
print()

# ---------------------------------------------------------
# 8. V12.6 momentum bridge
# ---------------------------------------------------------
momentum_result = evaluate_unified_observation_momentum(
    detailed_evidence
)

print(
    "Momentum Status:",
    momentum_result.get("Status")
)
print()

# ---------------------------------------------------------
# 9. V21.2.22-C evidence reconciliation
# ---------------------------------------------------------
reconciliation_result = reconcile_candidates(
    selected_qualification,
    detailed_evidence,
    momentum_result,
)

print(
    "Reconciliation Status:",
    reconciliation_result.get("Status")
)

reconciled_candidates = reconciliation_result.get(
    "Candidates",
    []
)

print(
    "Reconciled Candidates:",
    len(reconciled_candidates)
)
print()

# ---------------------------------------------------------
# 10. V21.2.22-D final evidence gate
# ---------------------------------------------------------
final_gate_result = evaluate_final_evidence_gate(
    reconciliation_result
)

print(
    "D Final Evidence Status:",
    final_gate_result.get("Status")
)

accepted = final_gate_result.get(
    "Accepted Candidates",
    []
)

rejected = final_gate_result.get(
    "Rejected Candidates",
    []
)

print("D Accepted:", len(accepted))
print("D Rejected:", len(rejected))
print()

for candidate in accepted:
    print(
        "  D ACCEPTED:",
        candidate.get("Trading Symbol"),
    )

for candidate in rejected:
    print(
        "  D REJECTED:",
        candidate.get("Trading Symbol"),
    )

print()

# ---------------------------------------------------------
# 11. V21.2.22-D.1 evidence-gated entry bridge
# ---------------------------------------------------------
bridge_result = build_entry_bridge(
    final_gate_result
)

print(
    "D.1 Bridge Status:",
    bridge_result.get("Status")
)
print(
    "D.1 Accepted:",
    bridge_result.get("Accepted Candidate Count")
)
print(
    "D.1 Rejected:",
    bridge_result.get("Rejected Candidate Count")
)
print(
    "D.1 Next Stage:",
    bridge_result.get("Next Stage")
)

print()

for candidate in bridge_result.get(
    "Accepted Candidates",
    [],
):
    print(
        "  BRIDGED:",
        candidate.get("Trading Symbol"),
        "| Entry Evaluation:",
        candidate.get("Entry Evaluation"),
    )

print()

# ---------------------------------------------------------
# 12. D.1 → B.1 authorization boundary
# ---------------------------------------------------------
d1_authorized_b1_result = build_d1_authorized_b1_result(
    selected_qualification,
    bridge_result,
)

print("D.1 → B.1 Authorization Status:",
      d1_authorized_b1_result.get("Status"))

print(
    "Original B.1 Qualified:",
    d1_authorized_b1_result.get(
        "Original B1 Qualified Candidate Count"
    ),
)

print(
    "D.1 Accepted:",
    d1_authorized_b1_result.get(
        "D1 Accepted Candidate Count"
    ),
)

print(
    "Authorized For V21.2.16:",
    d1_authorized_b1_result.get(
        "Authorized Candidate Count"
    ),
)

print(
    "Blocked By D.1:",
    d1_authorized_b1_result.get(
        "Rejected By D1 Count"
    ),
)

for candidate in d1_authorized_b1_result.get(
    "Qualified Candidates",
    [],
):
    print(
        "  AUTHORIZED:",
        candidate.get("Trading Symbol"),
    )

for candidate in d1_authorized_b1_result.get(
    "Rejected By D1 Candidates",
    [],
):
    print(
        "  BLOCKED BY D.1:",
        candidate.get("Trading Symbol"),
    )

print()

# ---------------------------------------------------------
# Safety assertions
# ---------------------------------------------------------
assert bridge_result.get("Status") == (
    "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE"
)

assert bridge_result.get("Live Order") is False
assert bridge_result.get("Paper Trade") is False

assert d1_authorized_b1_result.get("Status") == (
    "D1_AUTHORIZED_B1_RESULT_COMPLETE"
)

assert d1_authorized_b1_result.get("Live Order") is False
assert d1_authorized_b1_result.get("Paper Trade") is False

assert (
    d1_authorized_b1_result.get(
        "Authorized Candidate Count"
    )
    ==
    d1_authorized_b1_result.get(
        "D1 Accepted Candidate Count"
    )
)

for candidate in bridge_result.get(
    "Accepted Candidates",
    [],
):
    assert candidate.get("Evidence Gate") == "PASSED"
    assert candidate.get("Entry Evaluation") == "PENDING"
    assert candidate.get("Live Order") is False
    assert candidate.get("Paper Trade") is False

print("=" * 70)
print("V21.2.22-D.1 REAL-MARKET REGRESSION TEST PASS")
print("=" * 70)
print("Evidence Gate → Entry Bridge: VALID")
print("Live Order: False")
print("Paper Trade: False")
print("BUY/SELL: NOT EXECUTED")
print("=" * 70)
