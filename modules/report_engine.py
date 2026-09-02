"""
JKJ AI Report Engine v0.1

Wisdom Before Wealth.

This engine converts the complete JKJ AI analysis
into a clean, readable report.

It does not calculate scores or make decisions.
It only presents existing analysis clearly.
"""


def generate_report(analysis):
    """
    Generate a clean text report from the
    complete JKJ AI analysis.
    """

    symbol = analysis.get("Symbol", "UNKNOWN")

    market = analysis.get("Market Analysis", {})
    technical = analysis.get("Technical Analysis", {})
    opportunity = analysis.get("Opportunity Analysis", {})
    score = analysis.get("Score Analysis", {})
    risk = analysis.get("Risk Analysis", {})
    decision = analysis.get("Final Decision", {})

    lines = []

    lines.append("=" * 50)
    lines.append("JKJ AI TRADER — STOCK ANALYSIS")
    lines.append("=" * 50)

    lines.append("")
    lines.append(f"Symbol: {symbol}")

    # -----------------------------------------
    # MARKET
    # -----------------------------------------

    lines.append("")
    lines.append("MARKET")

    lines.append(
        f"Condition: {market.get('Market Condition', 'UNKNOWN')}"
    )

    lines.append(
        f"Score: {market.get('Standard Score', 0)} / 100"
    )

    # -----------------------------------------
    # TECHNICAL
    # -----------------------------------------

    lines.append("")
    lines.append("TECHNICAL")

    lines.append(
        f"Condition: {technical.get('Technical Condition', 'UNKNOWN')}"
    )

    lines.append(
        f"Score: {technical.get('Standard Score', 0)} / 100"
    )

    # -----------------------------------------
    # OPPORTUNITY
    # -----------------------------------------

    lines.append("")
    lines.append("OPPORTUNITY")

    lines.append(
        f"Condition: {opportunity.get('Opportunity Condition', 'UNKNOWN')}"
    )

    lines.append(
        f"Score: {opportunity.get('Standard Score', 0)} / 100"
    )

    # -----------------------------------------
    # COMBINED SCORE
    # -----------------------------------------

    lines.append("")
    lines.append("COMBINED OPPORTUNITY SCORE")

    lines.append(
        f"{score.get('Combined Opportunity Score', 0)} / 100"
    )

    # -----------------------------------------
    # RISK
    # -----------------------------------------

    lines.append("")
    lines.append("RISK")

    lines.append(
        f"Level: {risk.get('Risk Level', 'UNKNOWN')}"
    )

    lines.append(
        f"Score: {risk.get('Risk Score', 0)} / "
        f"{risk.get('Maximum Score', 0)}"
    )

    # -----------------------------------------
    # FINAL DECISION
    # -----------------------------------------

    lines.append("")
    lines.append("-" * 50)

    lines.append(
        f"FINAL JKJ DECISION: "
        f"{decision.get('JKJ Decision', 'UNKNOWN')}"
    )

    lines.append("-" * 50)

    # -----------------------------------------
    # DECISION REASONS
    # -----------------------------------------

    reasons = decision.get("Reasons", [])

    if reasons:

        lines.append("")
        lines.append("REASONS:")

        for reason in reasons:
            lines.append(f"• {reason}")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)