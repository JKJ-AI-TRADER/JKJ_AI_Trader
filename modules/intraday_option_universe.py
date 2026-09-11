"""
JKJ AI Trader
Intraday Option Universe Engine V1

Wisdom Before Wealth.

Purpose:
    Build a small, focused NIFTY option universe around
    the current ATM strike.

This engine does NOT:
    - fetch live prices
    - connect to Zerodha
    - place orders
    - make BUY decisions
    - calculate momentum

It only identifies which option contracts should be
examined by the next stage.

Initial universe:
    ATM - 2 strikes
    ATM - 1 strike
    ATM
    ATM + 1 strike
    ATM + 2 strikes

Both:
    CE
    PE
"""


def calculate_atm_strike(
    spot_price,
    strike_step
):
    """
    Calculate the nearest ATM strike.
    """

    try:
        spot_price = float(spot_price)
        strike_step = float(strike_step)

    except (TypeError, ValueError):

        raise ValueError(
            "Spot price and strike step must be numeric."
        )

    if spot_price <= 0:
        raise ValueError(
            "Spot price must be greater than zero."
        )

    if strike_step <= 0:
        raise ValueError(
            "Strike step must be greater than zero."
        )

    atm_strike = round(
        spot_price / strike_step
    ) * strike_step

    return int(atm_strike)


def build_nifty_option_universe(
    spot_price,
    strike_step,
    expiry,
    strikes_each_side=2
):
    """
    Build the initial NIFTY option universe.

    Parameters
    ----------
    spot_price : float
        Current NIFTY spot price.

    strike_step : int or float
        Strike interval.

    expiry : str
        Expiry identifier supplied by the caller.

    strikes_each_side : int
        Number of strikes above and below ATM.

    Returns
    -------
    dict
        Explainable option universe.
    """

    reasons = []
    warnings = []

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    try:

        spot_price = float(spot_price)
        strike_step = float(strike_step)
        strikes_each_side = int(
            strikes_each_side
        )

    except (TypeError, ValueError):

        return {
            "Status": "INVALID",
            "Underlying": "NIFTY",
            "Spot Price": spot_price,
            "ATM Strike": None,
            "Strike Step": strike_step,
            "Expiry": expiry,
            "Candidates": [],
            "Candidate Count": 0,
            "Reasons": [
                "Invalid numeric input."
            ],
            "Warnings": []
        }

    if spot_price <= 0:

        return {
            "Status": "INVALID",
            "Underlying": "NIFTY",
            "Spot Price": spot_price,
            "ATM Strike": None,
            "Strike Step": strike_step,
            "Expiry": expiry,
            "Candidates": [],
            "Candidate Count": 0,
            "Reasons": [
                "Spot price must be greater than zero."
            ],
            "Warnings": []
        }

    if strike_step <= 0:

        return {
            "Status": "INVALID",
            "Underlying": "NIFTY",
            "Spot Price": spot_price,
            "ATM Strike": None,
            "Strike Step": strike_step,
            "Expiry": expiry,
            "Candidates": [],
            "Candidate Count": 0,
            "Reasons": [
                "Strike step must be greater than zero."
            ],
            "Warnings": []
        }

    if not expiry:

        return {
            "Status": "INVALID",
            "Underlying": "NIFTY",
            "Spot Price": spot_price,
            "ATM Strike": None,
            "Strike Step": strike_step,
            "Expiry": expiry,
            "Candidates": [],
            "Candidate Count": 0,
            "Reasons": [
                "Expiry is required."
            ],
            "Warnings": []
        }

    if strikes_each_side < 0:

        return {
            "Status": "INVALID",
            "Underlying": "NIFTY",
            "Spot Price": spot_price,
            "ATM Strike": None,
            "Strike Step": strike_step,
            "Expiry": expiry,
            "Candidates": [],
            "Candidate Count": 0,
            "Reasons": [
                "Strikes each side cannot be negative."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # ATM
    # -----------------------------------------

    atm_strike = calculate_atm_strike(
        spot_price,
        strike_step
    )

    reasons.append(
        f"NIFTY spot {spot_price:.2f} mapped "
        f"to ATM strike {atm_strike}."
    )

    # -----------------------------------------
    # STRIKE RANGE
    # -----------------------------------------

    strikes = []

    for offset in range(
        -strikes_each_side,
        strikes_each_side + 1
    ):

        strike = int(
            atm_strike
            + (offset * strike_step)
        )

        strikes.append(strike)

    # -----------------------------------------
    # BUILD CE / PE CANDIDATES
    # -----------------------------------------

    candidates = []

    for strike in strikes:

        for option_type in (
            "CE",
            "PE"
        ):

            candidates.append(
                {
                    "Underlying": "NIFTY",
                    "Expiry": expiry,
                    "Strike": strike,
                    "Option Type": option_type,
                    "Distance From ATM":
                        strike - atm_strike
                }
            )

    reasons.append(
        f"Universe contains "
        f"{len(strikes)} strikes and "
        f"{len(candidates)} option contracts."
    )

    warnings.append(
        "Contracts are candidates only. "
        "Liquidity, spread, momentum and cost "
        "checks must be performed before entry."
    )

    return {
        "Status": "READY",
        "Underlying": "NIFTY",
        "Spot Price": spot_price,
        "ATM Strike": atm_strike,
        "Strike Step": strike_step,
        "Expiry": expiry,
        "Strikes": strikes,
        "Candidates": candidates,
        "Candidate Count": len(candidates),
        "Reasons": reasons,
        "Warnings": warnings
    }