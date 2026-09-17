"""
JKJ AI Trader
NIFTY Option Momentum Confirmation — V12.6 Stage 3

Purpose:
Evaluate whether persistent option movement has supporting
observable evidence.

This stage does NOT:
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- generate trading signals
- place orders
- modify main.py
- modify frozen JKJ modules

Confirmation rules:

CONFIRMED:
- Persistence is PERSISTENT
- Price Movement Evidence is True
- Volume Evidence is True

PARTIALLY_CONFIRMED:
- Persistence is PERSISTENT
- Price Movement Evidence is True
- Volume Evidence is False

NOT_CONFIRMED:
- Persistence is not PERSISTENT
- or price movement evidence is absent

OI and NIFTY relationship are reported as supporting evidence
but do not independently determine confirmation.
"""


def evaluate_momentum_confirmation(
    momentum_evidence,
    momentum_sequence,
):
    """
    Combine V12.6 Stage 1 evidence with V12.6 Stage 2
    persistence information.
    """

    if not isinstance(momentum_evidence, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Momentum evidence must be a dictionary.",
        }

    if not isinstance(momentum_sequence, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Momentum sequence must be a dictionary.",
        }

    if momentum_evidence.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Momentum evidence must have Status EVALUATED.",
        }

    if momentum_sequence.get("Status") not in {
        "PERSISTENT",
        "NOT_PERSISTENT",
    }:
        return {
            "Status": "REJECTED",
            "Reason": (
                "Momentum sequence must have Status "
                "PERSISTENT or NOT_PERSISTENT."
            ),
        }

    required_evidence_fields = [
        "Price Movement Evidence",
        "NIFTY Movement Evidence",
        "Volume Evidence",
        "Open Interest Evidence",
        "Movement Relationship",
    ]

    for field in required_evidence_fields:
        if field not in momentum_evidence:
            return {
                "Status": "REJECTED",
                "Reason": f"Missing evidence field: {field}.",
            }

    if "Persistence Status" not in momentum_sequence:
        return {
            "Status": "REJECTED",
            "Reason": "Missing Persistence Status.",
        }

    persistence_status = momentum_sequence["Persistence Status"]

    if persistence_status not in {
        "PERSISTENT",
        "NOT_PERSISTENT",
    }:
        return {
            "Status": "REJECTED",
            "Reason": "Invalid Persistence Status.",
        }

    price_evidence = momentum_evidence[
        "Price Movement Evidence"
    ]

    volume_evidence = momentum_evidence[
        "Volume Evidence"
    ]

    nifty_evidence = momentum_evidence[
        "NIFTY Movement Evidence"
    ]

    oi_evidence = momentum_evidence[
        "Open Interest Evidence"
    ]

    relationship = momentum_evidence[
        "Movement Relationship"
    ]

    if persistence_status == "PERSISTENT" and price_evidence:
        if volume_evidence:
            confirmation = "CONFIRMED"
        else:
            confirmation = "PARTIALLY_CONFIRMED"
    else:
        confirmation = "NOT_CONFIRMED"

    return {
        "Status": "EVALUATED",
        "Trading Symbol": momentum_evidence.get("Trading Symbol"),
        "Underlying": momentum_evidence.get("Underlying"),
        "Expiry": momentum_evidence.get("Expiry"),
        "Strike": momentum_evidence.get("Strike"),
        "Option Type": momentum_evidence.get("Option Type"),
        "Option Direction": momentum_evidence.get(
            "Option Direction"
        ),
        "Persistence Status": persistence_status,
        "Price Movement Evidence": price_evidence,
        "NIFTY Movement Evidence": nifty_evidence,
        "Volume Evidence": volume_evidence,
        "Open Interest Evidence": oi_evidence,
        "Movement Relationship": relationship,
        "Momentum Confirmation": confirmation,
    }