"""
JKJ AI Trader
NIFTY Option Contract Selector — Stage 1

Purpose:
Select a small set of NIFTY option contracts around
the current NIFTY spot price.

This stage does NOT:
- collect live option prices
- calculate momentum
- calculate opportunity scores
- make BUY/SELL decisions
- place orders
- modify main.py
"""

def select_nearby_contracts(
    instruments,
    nifty_spot,
    expiry,
    contracts_per_side=2,
):
    """
    Select nearby CE and PE contracts around NIFTY spot.

    Parameters
    ----------
    instruments : list
        Zerodha NFO instrument records.

    nifty_spot : float
        Current NIFTY spot price.

    expiry : str or date
        Required option expiry. Accepts a YYYY-MM-DD string
        or a Python date object from Zerodha.

    contracts_per_side : int
        Number of CE and PE contracts to select.

    Returns
    -------
    dict
        Selection result.
    """

    if not isinstance(instruments, list):
        return {
            "Status": "REJECTED",
            "Reason": "Instruments must be a list.",
        }

    if not isinstance(nifty_spot, (int, float)):
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY spot must be numeric.",
        }

    if nifty_spot <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "NIFTY spot must be greater than zero.",
        }

    if expiry is None:
        return {
        "Status": "REJECTED",
        "Reason": "Expiry is required.",
    }

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

    expiry_options = [
        item
        for item in instruments
        if isinstance(item, dict)
        and item.get("name") == "NIFTY"
        and str(item.get("expiry")) == str(expiry)
        and item.get("instrument_type") in ("CE", "PE")
        and isinstance(item.get("strike"), (int, float))
        and item.get("strike") > 0
    ]

    if not expiry_options:
        return {
            "Status": "REJECTED",
            "Reason": "No NIFTY option contracts found for the selected expiry.",
        }

    ce_contracts = [
        item
        for item in expiry_options
        if item.get("instrument_type") == "CE"
    ]

    pe_contracts = [
        item
        for item in expiry_options
        if item.get("instrument_type") == "PE"
    ]

    ce_contracts.sort(
        key=lambda item: abs(
            item.get("strike") - nifty_spot
        )
    )

    pe_contracts.sort(
        key=lambda item: abs(
            item.get("strike") - nifty_spot
        )
    )

    selected_ce = ce_contracts[
        :contracts_per_side
    ]

    selected_pe = pe_contracts[
        :contracts_per_side
    ]

    selected_contracts = (
        selected_ce + selected_pe
    )

    if len(selected_contracts) == 0:
        return {
            "Status": "REJECTED",
            "Reason": "No contracts could be selected.",
        }

    return {
        "Status": "SELECTED",
        "NIFTY Spot": nifty_spot,
        "Expiry": expiry,
        "Contracts Per Side": contracts_per_side,
        "Contracts": selected_contracts,
    }