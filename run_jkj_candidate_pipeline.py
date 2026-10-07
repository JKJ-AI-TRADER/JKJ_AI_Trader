from modules.jkj_daily_zerodha_auth import authenticate_today
from modules.nifty_option_v21_2_19_persistent_observer import run_persistent_observer
from modules.nifty_option_v21_2_20_candidate_qualification import qualify_candidates
from modules.nifty_option_v21_2_22_b_candidate_refresh_v2 import refresh_developing_candidates_v2
from modules.nifty_option_v21_2_22_b1_candidate_selection import select_candidates

print("=" * 70)
print("JKJ REAL-MARKET CANDIDATE PIPELINE")
print("V21.2.19 -> V21.2.20 -> B v2 -> B.1")
print("=" * 70)

auth = authenticate_today()
kite = auth.get("Kite")

if kite is None:
    print("ERROR: Kite session unavailable.")
    raise SystemExit(1)

print("Zerodha:", auth.get("Status"))
print("Kite: READY")
print("Live Order: False")
print("Paper Trade: False")
print()

observer_result = run_persistent_observer(
    kite,
    interval_seconds=15,
    max_observations=4,
    strikes_each_side=10,
)

if observer_result.get("Status") != "PERSISTENT_OBSERVER_COMPLETE":
    print("Observer failed:", observer_result.get("Status"))
    raise SystemExit(1)

lifecycle_store = observer_result.get("Candidate Lifecycle", {})

print()
print("=" * 70)
print("V21.2.20 CANDIDATE QUALIFICATION")
print("=" * 70)

qualification_result = qualify_candidates(lifecycle_store)

print("Status:", qualification_result.get("Status"))
print("Observed Candidates:", qualification_result.get("Observed Candidate Count"))
print("Qualified Candidates:", qualification_result.get("Qualified Candidate Count"))

print()
print("=" * 70)
print("V21.2.22-B v2 DEVELOPING REFRESH")
print("=" * 70)

b2_refresh = refresh_developing_candidates_v2(lifecycle_store)

print("Status:", b2_refresh.get("Status"))
print("Candidate Count:", b2_refresh.get("Candidate Count"))
print("Category Counts:", b2_refresh.get("Category Counts"))

print()
print("=" * 70)
print("V21.2.22-B.1 CANDIDATE SELECTION")
print("=" * 70)

selection_result = select_candidates(
    b2_refresh,
    max_candidates=3,
)

print("Status:", selection_result.get("Status"))
print("Eligible Candidates:", selection_result.get("Eligible Candidate Count"))
print("Selected Count:", selection_result.get("Selected Count"))

for candidate in selection_result.get("Selected Candidates", []):
    print(
        candidate.get("Selection Rank"),
        "|",
        candidate.get("Trading Symbol"),
        "| Category:",
        candidate.get("Category"),
        "| State:",
        candidate.get("Lifecycle State"),
        "| Score:",
        candidate.get("Ranking Score"),
    )

print()
print("=" * 70)
print("PIPELINE COMPLETE")
print("=" * 70)
print("Candidate != Trade")
print("Live Order: False")
print("Paper Trade: False")
