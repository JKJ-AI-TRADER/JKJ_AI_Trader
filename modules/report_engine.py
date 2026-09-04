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
    momentum = analysis.get("Momentum Analysis", {})
    score = analysis.get("Score Analysis", {})
    risk = analysis.get("Risk Analysis", {})
    decision = analysis.get("Final Decision", {})

    holding_status = analysis.get(
        "Holding Status",
        False
    )

    purchase_price = analysis.get(
        "Purchase Price",
        0
    )

    current_price = analysis.get(
        "Current Price",
        0
    )

    profit_loss_percentage = analysis.get(
        "Profit/Loss Percentage",
        0
    )

    lines = []

    lines.append("=" * 50)
    lines.append("JKJ AI TRADER — STOCK ANALYSIS")
    lines.append("=" * 50)

    lines.append("")
    lines.append(f"Symbol: {symbol}")

    # -----------------------------------------
    # EXISTING HOLDING POSITION
    # -----------------------------------------

    if holding_status:

        lines.append("")
        lines.append("EXISTING HOLDING POSITION")

        lines.append(
            f"Purchase Price: ₹{purchase_price:.2f}"
        )

        lines.append(
            f"Current Price: ₹{current_price:.2f}"
        )

        lines.append(
            f"Profit/Loss: {profit_loss_percentage:.2f}%"
        )

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

    lines.append(
        f"State: {market.get('Market State', 'UNKNOWN')}"
    )

    market_explanation = market.get(
        "Explanation",
        []
    )

    if market_explanation:

        lines.append("")
        lines.append("MARKET SIGNALS:")

        for item in market_explanation:
            lines.append(f"• {item}")

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
    # MOMENTUM
    # -----------------------------------------

    lines.append("")
    lines.append("MOMENTUM")

    lines.append(
        f"Condition: {momentum.get('Momentum Condition', 'UNKNOWN')}"
    )

    lines.append(
        f"Score: {momentum.get('Standard Score', 0)} / 100"
    )

    momentum_explanation = momentum.get(
        "Explanation",
        []
    )

    if momentum_explanation:

        lines.append("")
        lines.append("MOMENTUM SIGNALS:")

        for item in momentum_explanation:
            lines.append(f"• {item}")

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

    # -----------------------------------------
    # CONFIDENCE
    # -----------------------------------------

    lines.append("")
    lines.append(
        f"CONFIDENCE: {decision.get('Confidence', 0)}%"
    )

    # -----------------------------------------
    # POSITIVE SIGNALS
    # -----------------------------------------

    positive_signals = decision.get(
        "Positive Signals",
        decision.get("Positive Evidence", [])
    )

    if positive_signals:

        lines.append("")
        lines.append("POSITIVE SIGNALS:")

        for signal in positive_signals:
            lines.append(f"• {signal}")

    # -----------------------------------------
    # WARNINGS
    # -----------------------------------------

    warnings = decision.get(
        "Warnings",
        decision.get("Risk Warnings", [])
    )

    if warnings:

        lines.append("")
        lines.append("WARNINGS:")

        for warning in warnings:
            lines.append(f"• {warning}")

    # -----------------------------------------
    # MISSING CONFIRMATION
    # -----------------------------------------

    missing_confirmation = decision.get(
        "Missing Confirmation",
        []
    )

    if missing_confirmation:

        lines.append("")
        lines.append("MISSING CONFIRMATION:")

        for item in missing_confirmation:
            lines.append(f"• {item}")

    # -----------------------------------------
    # NEXT REQUIRED SIGNAL
    # -----------------------------------------

    next_signal = decision.get(
        "Next Required Signal",
        ""
    )

    if next_signal:

        lines.append("")
        lines.append("NEXT REQUIRED SIGNAL:")
        lines.append(next_signal)

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)