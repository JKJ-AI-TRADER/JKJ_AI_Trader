def create_investor_rules(
    max_loss_percent,
    target_1_percent,
    target_2_percent,
    holding_period_days,
    trailing_stop_percent
):
    """
    JKJ AI Investor Rule Engine v0.1

    Investor defines protection boundaries.
    JKJ AI enforces discipline.

    Wisdom Before Wealth.
    """

    return {
        "Maximum Loss %": max_loss_percent,
        "Target 1 %": target_1_percent,
        "Target 2 %": target_2_percent,
        "Holding Period Days": holding_period_days,
        "Trailing Stop %": trailing_stop_percent
    }


def evaluate_position(
    buy_price,
    current_price,
    rules
):
    """
    Evaluate current holding against investor rules.
    """

    profit_loss_percent = (
        (current_price - buy_price)
        / buy_price
    ) * 100


    decision = "HOLD"
    reasons = []


    if profit_loss_percent <= -rules["Maximum Loss %"]:
        decision = "EXIT REVIEW"
        reasons.append(
            "Maximum loss limit exceeded"
        )


    elif profit_loss_percent >= rules["Target 2 %"]:
        decision = "BOOK PROFIT"
        reasons.append(
            "Second profit target achieved"
        )


    elif profit_loss_percent >= rules["Target 1 %"]:
        decision = "PARTIAL PROFIT"
        reasons.append(
            "First profit target achieved"
        )


    else:
        reasons.append(
            "Position within investor limits"
        )


    return {
        "Current Return %": round(profit_loss_percent,2),
        "JKJ Rule Decision": decision,
        "Reasons": reasons
    }
