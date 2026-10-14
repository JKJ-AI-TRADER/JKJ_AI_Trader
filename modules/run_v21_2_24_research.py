
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.jkj_daily_zerodha_auth import authenticate_today
from modules.nifty_option_v21_2_23_multi_expiry_discovery import (
    run_multi_expiry_discovery,
)
from modules.nifty_option_v21_2_23_1_discovery_selector import (
    select_discovery_candidates,
)
from modules.nifty_option_v21_2_24_1_one_hour_observer import (
    observe_for_one_hour,
)
from modules.nifty_option_v21_2_24_2_movement_analyzer import (
    analyze_one_hour_observation,
)


OUTPUT_DIR = Path("research_data")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 70)
    print("JKJ V21.2.24 RESEARCH RUN")
    print("Discovery → Selection → One-Hour Observation → Analysis")
    print("RESEARCH ONLY / NO ORDERS / NO PAPER TRADES")
    print("=" * 70)

    print("\n[0] Zerodha Authentication")

    session_result = authenticate_today()

    if not isinstance(session_result, dict):
        print("ERROR: Unexpected Zerodha authentication result.")
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("ERROR: Zerodha Kite session unavailable.")
        print("Authentication result:", session_result)
        return

    print("Kite session: READY")
    print("Live Order: False")
    print("Paper Trade: False")

    print("\n[1] Multi-Expiry Discovery")

    discovery = run_multi_expiry_discovery(
        kite,
        observation_count=4,
        interval_seconds=15,
    )

    if discovery.get("Status") != "MULTI_EXPIRY_DISCOVERY_COMPLETE":
        print("Discovery failed:", discovery.get("Status"))
        return

    print("\n[2] Discovery Candidate Selection")

    selection = select_discovery_candidates(
        discovery,
        max_selected=10,
    )

    if selection.get("Status") != "DISCOVERY_CANDIDATE_SELECTION_COMPLETE":
        print("Selection failed:", selection.get("Status"))
        return

    candidates = selection.get("Selected Candidates", [])

    print(f"Selected candidates: {len(candidates)}")

    if not candidates:
        print("No discovery candidates.")
        return

    print("\n[3] One-Hour Observation")
    print("Duration: 60 minutes")
    print("Interval: 60 seconds")
    print("Complete Observation History will be retained.")

    observation = observe_for_one_hour(
        kite,
        selection,
        duration_minutes=60,
        interval_seconds=60,
    )

    if observation.get("Status") != "ONE_HOUR_OBSERVATION_COMPLETE":
        print("Observation failed:", observation.get("Status"))
        return

    print("\n[4] Saving Complete Observation History")

    timestamp = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y%m%d_%H%M%S")

    raw_file = OUTPUT_DIR / f"v21_2_24_observation_{timestamp}.json"

    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(observation, f, indent=2, default=str)

    print(f"Saved: {raw_file}")

    print("\n[5] V21.2.24.2 Movement / Peak / Giveback Analysis")

    analysis = analyze_one_hour_observation(observation)

    analysis_file = OUTPUT_DIR / f"v21_2_24_analysis_{timestamp}.json"

    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"Saved: {analysis_file}")

    print("\n" + "=" * 70)
    print("V21.2.24 RESEARCH COMPLETE")
    print("=" * 70)

    print("Observation Status:", observation.get("Status"))
    print("Analysis Status:", analysis.get("Status"))
    print("Candidates:", observation.get("Candidate Count"))
    print("Checkpoints:", list(observation.get("Checkpoints", {}).keys()))
    print("Live Order:", observation.get("Live Order"))
    print("Paper Trade:", observation.get("Paper Trade"))

    print("\nResearch files:")
    print(raw_file)
    print(analysis_file)


if __name__ == "__main__":
    main()
