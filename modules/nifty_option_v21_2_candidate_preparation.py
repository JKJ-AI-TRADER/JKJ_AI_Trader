"""
JKJ AI Trader
V21.2.5 — NIFTY Candidate Preparation

Purpose:
Prepare a small NIFTY CE/PE observation universe during
pre-market preparation.

This module reuses:
- Existing secure Zerodha session manager
- Existing NFO instrument loading
- Existing NIFTY option contract selector

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V21.1 modules
- modify main.py
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)


def prepare_nifty_candidates(
    contracts_per_side=2,
):
    """
    Prepare nearby NIFTY CE and PE contracts.

    Returns a read-only observation universe.
    """

    if not isinstance(contracts_per_side, int):
        return {
            "Status": "REJECTED",
            "Reason": "Contracts per side must be an integer.",
        }

    if contracts_per_side <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Contracts per side must be greater than zero.",
        }

    # --------------------------------------------------
    # STEP 1 — EXISTING ZERODHA SESSION
    # --------------------------------------------------

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return {
            "Status": "FAILED",
            "Reason": "Unexpected Zerodha session result.",
            "Live Order": False,
            "Paper Trade": False,
        }

    session_status = session_result.get("Status")

    if session_status not in (
        "SESSION_REUSED",
        "SESSION_CREATED",
        "AUTHENTICATED",
    ):
        return {
            "Status": "FAILED",
            "Reason": session_result.get(
                "Reason",
                "Zerodha session was not established.",
            ),
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    kite = session_result.get("Kite")

    if kite is None:
        return {
            "Status": "FAILED",
            "Reason": "Kite session object is missing.",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 2 — NFO INSTRUMENTS
    # --------------------------------------------------

    try:
        instruments = kite.instruments("NFO")

    except Exception as error:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to load NFO instruments: {error}",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(instruments, list) or not instruments:
        return {
            "Status": "FAILED",
            "Reason": "NFO instrument list unavailable or empty.",
            "Session Status": session_status,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 3 — NIFTY SPOT
    # --------------------------------------------------

    try:
        nifty_quote = kite.ltp(
            "NSE:NIFTY 50"
        )

        nifty_spot = nifty_quote[
            "NSE:NIFTY 50"
        ]["last_price"]

    except Exception as error:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to obtain NIFTY spot: {error}",
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        return {
            "Status": "FAILED",
            "Reason": "Invalid NIFTY spot price.",
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "NIFTY Spot": nifty_spot,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 4 — FILTER NIFTY OPTIONS
    # --------------------------------------------------

    nifty_options = [
        item
        for item in instruments
        if isinstance(item, dict)
        and item.get("name") == "NIFTY"
        and item.get("instrument_type") in ("CE", "PE")
    ]

    if not nifty_options:
        return {
            "Status": "FAILED",
            "Reason": "No NIFTY option contracts found.",
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "NIFTY Spot": nifty_spot,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 5 — IDENTIFY NEAREST AVAILABLE EXPIRY
    # --------------------------------------------------

    expiries = sorted({
        item.get("expiry")
        for item in nifty_options
        if item.get("expiry")
    })

    if not expiries:
        return {
            "Status": "FAILED",
            "Reason": "No NIFTY option expiry found.",
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "NIFTY Spot": nifty_spot,
            "Live Order": False,
            "Paper Trade": False,
        }

    selected_expiry = expiries[0]

    # --------------------------------------------------
    # STEP 6 — REUSE EXISTING CONTRACT SELECTOR
    # --------------------------------------------------

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=contracts_per_side,
    )

    if selection.get("Status") != "SELECTED":
        return {
            "Status": "FAILED",
            "Reason": selection.get(
                "Reason",
                "NIFTY option contract selection failed.",
            ),
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "NIFTY Spot": nifty_spot,
            "Expiry": selected_expiry,
            "Live Order": False,
            "Paper Trade": False,
        }

    contracts = selection.get(
        "Contracts",
        []
    )

    ce_candidates = [
        contract
        for contract in contracts
        if contract.get("instrument_type") == "CE"
    ]

    pe_candidates = [
        contract
        for contract in contracts
        if contract.get("instrument_type") == "PE"
    ]

    if not ce_candidates or not pe_candidates:
        return {
            "Status": "FAILED",
            "Reason": "Both CE and PE candidates are required.",
            "Session Status": session_status,
            "NFO Instruments": len(instruments),
            "NIFTY Spot": nifty_spot,
            "Expiry": selected_expiry,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 7 — VALIDATE CANDIDATE IDENTITY
    # --------------------------------------------------

    for contract in contracts:

        required_fields = (
            "tradingsymbol",
            "instrument_token",
            "name",
            "expiry",
            "strike",
            "instrument_type",
        )

        missing_fields = [
            field
            for field in required_fields
            if contract.get(field) is None
        ]

        if missing_fields:
            return {
                "Status": "FAILED",
                "Reason": (
                    "Candidate identity incomplete: "
                    f"{missing_fields}"
                ),
                "Session Status": session_status,
                "NFO Instruments": len(instruments),
                "NIFTY Spot": nifty_spot,
                "Expiry": selected_expiry,
                "Live Order": False,
                "Paper Trade": False,
            }

        if contract.get("name") != "NIFTY":
            return {
                "Status": "FAILED",
                "Reason": "Candidate underlying is not NIFTY.",
                "Live Order": False,
                "Paper Trade": False,
            }

        if str(contract.get("expiry")) != str(
            selected_expiry
        ):
            return {
                "Status": "FAILED",
                "Reason": "Candidate expiry does not match selected expiry.",
                "Live Order": False,
                "Paper Trade": False,
            }

    # --------------------------------------------------
    # STEP 8 — RETURN OBSERVATION UNIVERSE
    # --------------------------------------------------

    return {
        "Status": "CANDIDATES_READY",
        "Session Status": session_status,
        "NFO Instruments": len(instruments),
        "NIFTY Spot": nifty_spot,
        "Expiry": selected_expiry,
        "Contracts Per Side": contracts_per_side,
        "CE Candidates": ce_candidates,
        "PE Candidates": pe_candidates,
        "All Candidates": contracts,
        "Contract Identity": "VALIDATED",
        "Observation Universe": "READY",
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print("=" * 70)
    print(
        "JKJ AI TRADER — "
        "V21.2.5 NIFTY CANDIDATE PREPARATION TEST"
    )
    print("=" * 70)

    result = prepare_nifty_candidates(
        contracts_per_side=2
    )

    for key, value in result.items():

        if key in (
            "CE Candidates",
            "PE Candidates",
            "All Candidates",
        ):
            print(
                f"{key}: "
                f"{len(value) if isinstance(value, list) else value}"
            )

            if isinstance(value, list):
                for contract in value:
                    print(
                        "  ",
                        contract.get("tradingsymbol"),
                        "|",
                        contract.get("instrument_type"),
                        "| Strike:",
                        contract.get("strike"),
                        "| Token:",
                        contract.get("instrument_token"),
                    )

        else:
            print(f"{key}: {value}")

    print("=" * 70)
