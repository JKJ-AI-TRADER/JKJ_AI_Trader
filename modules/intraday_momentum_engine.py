"""
JKJ AI Intraday Momentum Engine v0.1

Wisdom Before Wealth.

This engine identifies whether an intraday price move
is developing strongly enough to become an opportunity.

It does NOT place trades.

It does NOT make the final BUY decision.

It evaluates:

- Price acceleration
- Volume acceleration
- Underlying confirmation
- Higher-high / higher-low structure
- Liquidity and spread
- Exhaustion
- Remaining profit potential
- Risk / reward

The output is an explainable Momentum Score.
"""


def analyse_intraday_momentum(
    history,
    underlying_history=None,
    spread_percentage=None,
    remaining_profit_percentage=None,
    risk_reward_ratio=None
):
    """
    Analyse intraday momentum from historical OHLCV data.

    Parameters
    ----------
    history : pandas.DataFrame
        Expected columns:
        Open, High, Low, Close, Volume

    underlying_history : pandas.DataFrame, optional
        Historical underlying data used for confirmation.

    spread_percentage : float, optional
        Current bid/ask spread as a percentage.

    remaining_profit_percentage : float, optional
        Estimated remaining price movement available
        after the current entry area.

    risk_reward_ratio : float, optional
        Expected reward divided by defined risk.

    Returns
    -------
    dict
        Explainable momentum assessment.
    """

    reasons = []
    warnings = []

    # -----------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------

    if history is None:

        return {
            "Momentum Status": "NO TRADE",
            "Momentum Strength": "UNKNOWN",
            "Momentum Score": 0,
            "Trade Candidate": False,
            "Reasons": [
                "No intraday price history was provided."
            ],
            "Warnings": []
        }

    if len(history) < 20:

        return {
            "Momentum Status": "NO TRADE",
            "Momentum Strength": "UNKNOWN",
            "Momentum Score": 0,
            "Trade Candidate": False,
            "Reasons": [
                "Insufficient intraday history for "
                "momentum analysis."
            ],
            "Warnings": []
        }

    required_columns = [
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in required_columns:

        if column not in history.columns:

            return {
                "Momentum Status": "NO TRADE",
                "Momentum Strength": "UNKNOWN",
                "Momentum Score": 0,
                "Trade Candidate": False,
                "Reasons": [
                    f"Required column missing: {column}."
                ],
                "Warnings": []
            }

    # -----------------------------------------
    # CLEAN DATA
    # -----------------------------------------

    data = history[
        required_columns
    ].copy()

    data = data.dropna(
        subset=required_columns
    )

    if len(data) < 20:

        return {
            "Momentum Status": "NO TRADE",
            "Momentum Strength": "UNKNOWN",
            "Momentum Score": 0,
            "Trade Candidate": False,
            "Reasons": [
                "Insufficient valid intraday data."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # CURRENT PRICE
    # -----------------------------------------

    current_price = float(
        data["Close"].iloc[-1]
    )

    if current_price <= 0:

        return {
            "Momentum Status": "NO TRADE",
            "Momentum Strength": "UNKNOWN",
            "Momentum Score": 0,
            "Trade Candidate": False,
            "Reasons": [
                "Current price is invalid."
            ],
            "Warnings": []
        }

    # -----------------------------------------
    # -----------------------------------------
    # 1. PRICE ACCELERATION — 20 POINTS
    # -----------------------------------------

    recent_closes = data["Close"]

    # Keep the 5-bar price change for later exhaustion analysis.
    if len(recent_closes) >= 6:

        price_5_bars_ago = float(
            recent_closes.iloc[-6]
        )

        price_change = (
            (current_price - price_5_bars_ago)
            / price_5_bars_ago
        ) * 100

    else:

        price_change = 0

    # V0.2 acceleration:
    # Compare two equal 3-bar price movements.
    #
    # Earlier movement:
    #     close[-7] -> close[-4]
    #
    # Latest movement:
    #     close[-4] -> close[-1]
    #
    # Positive difference means the latest movement
    # is becoming stronger.

    if len(recent_closes) >= 7:

        earlier_start = float(
            recent_closes.iloc[-7]
        )

        earlier_end = float(
            recent_closes.iloc[-4]
        )

        latest_start = float(
            recent_closes.iloc[-4]
        )

        latest_end = float(
            recent_closes.iloc[-1]
        )

        if earlier_start > 0 and latest_start > 0:

            earlier_velocity = (
                (earlier_end - earlier_start)
                / earlier_start
            ) * 100

            latest_velocity = (
                (latest_end - latest_start)
                / latest_start
            ) * 100

            acceleration_change = (
                latest_velocity
                - earlier_velocity
            )

        else:

            earlier_velocity = 0
            latest_velocity = 0
            acceleration_change = 0

    else:

        earlier_velocity = 0
        latest_velocity = 0
        acceleration_change = 0

    # V0.2 currently remains focused on bullish
    # acceleration. Bearish direction will be added
    # in the separate Direction stage.

    if latest_velocity <= 0:

        price_score = 0

        reasons.append(
            "Price is not currently showing positive "
            "short-term movement."
        )

    elif acceleration_change <= 0:

        price_score = 5

        reasons.append(
            "Price is moving positively, but "
            "short-term acceleration is slowing."
        )

    elif acceleration_change < 0.10:

        price_score = 10

        reasons.append(
            "Price is showing developing acceleration."
        )

    elif acceleration_change < 0.25:

        price_score = 15

        reasons.append(
            "Price is showing strong acceleration."
        )

    else:

        price_score = 20

        reasons.append(
            "Price is showing exceptional acceleration "
            "with the latest movement strengthening."
        )

    # 2. VOLUME ACCELERATION — 15 POINTS
    # -----------------------------------------

    volume = data["Volume"]

    if len(volume) >= 20:

        recent_volume = float(
            volume.tail(5).mean()
        )

        previous_volume = float(
            volume.iloc[-15:-5].mean()
        )

        if previous_volume > 0:

            volume_change = (
                (recent_volume - previous_volume)
                / previous_volume
            ) * 100

        else:

            volume_change = 0

    else:

        volume_change = 0

    if volume_change <= 0:

        volume_score = 0

        reasons.append(
            "Volume is not accelerating."
        )

    elif volume_change < 20:

        volume_score = 4

        reasons.append(
            "Volume shows mild improvement."
        )

    elif volume_change < 40:

        volume_score = 8

        reasons.append(
            "Volume is increasing with the price movement."
        )

    elif volume_change < 75:

        volume_score = 12

        reasons.append(
            "Volume is accelerating strongly."
        )

    else:

        volume_score = 15

        reasons.append(
            "Volume is accelerating exceptionally."
        )

    # -----------------------------------------
    # 3. UNDERLYING CONFIRMATION — 15 POINTS
    # -----------------------------------------

    underlying_score = 0

    if underlying_history is None:

        underlying_score = 5

        reasons.append(
            "Underlying confirmation is unavailable; "
            "only partial confirmation is credited."
        )

        warnings.append(
            "Underlying confirmation should be available "
            "before live entry."
        )

    else:

        if len(underlying_history) >= 6:

            underlying_close = (
                underlying_history["Close"]
            )

            underlying_current = float(
                underlying_close.iloc[-1]
            )

            underlying_previous = float(
                underlying_close.iloc[-6]
            )

            if underlying_previous > 0:

                underlying_change = (
                    (
                        underlying_current
                        - underlying_previous
                    )
                    / underlying_previous
                ) * 100

            else:

                underlying_change = 0

            if underlying_change > 0.50:

                underlying_score = 15

                reasons.append(
                    "Underlying instrument strongly "
                    "confirms the move."
                )

            elif underlying_change > 0:

                underlying_score = 10

                reasons.append(
                    "Underlying instrument confirms "
                    "the direction of the move."
                )

            elif underlying_change > -0.25:

                underlying_score = 5

                reasons.append(
                    "Underlying instrument is relatively "
                    "stable while the instrument moves."
                )

            else:

                underlying_score = 0

                reasons.append(
                    "Underlying instrument is moving "
                    "against the current price direction."
                )

        else:

            underlying_score = 5

            reasons.append(
                "Underlying history is insufficient "
                "for full confirmation."
            )

            warnings.append(
                "Obtain more underlying data before entry."
            )

    # -----------------------------------------
    # 4. PRICE STRUCTURE — 10 POINTS
    # -----------------------------------------

    structure_score = 0

    recent_data = data.tail(6)

    highs = recent_data["High"].tolist()
    lows = recent_data["Low"].tolist()

    higher_highs = 0
    higher_lows = 0

    for i in range(1, len(highs)):

        if highs[i] > highs[i - 1]:

            higher_highs += 1

        if lows[i] > lows[i - 1]:

            higher_lows += 1

    if (
        higher_highs >= 4
        and higher_lows >= 4
    ):

        structure_score = 10

        reasons.append(
            "Price structure shows strong "
            "higher-high and higher-low formation."
        )

    elif (
        higher_highs >= 3
        and higher_lows >= 3
    ):

        structure_score = 8

        reasons.append(
            "Price structure shows developing "
            "higher highs and higher lows."
        )

    elif (
        higher_highs >= 2
        and higher_lows >= 2
    ):

        structure_score = 6

        reasons.append(
            "Price structure shows moderate "
            "upward development."
        )

    elif higher_highs >= 2:

        structure_score = 3

        reasons.append(
            "Some upward price structure is present."
        )

    else:

        structure_score = 0

        reasons.append(
            "Higher-high / higher-low structure "
            "is not sufficiently confirmed."
        )

    # -----------------------------------------
    # 5. LIQUIDITY & SPREAD — 10 POINTS
    # -----------------------------------------

    if spread_percentage is None:

        liquidity_score = 5

        reasons.append(
            "Spread information is unavailable; "
            "only partial liquidity score is credited."
        )

        warnings.append(
            "Live spread data is required before execution."
        )

    else:

        try:

            spread = float(
                spread_percentage
            )

            if spread <= 0.10:

                liquidity_score = 10

                reasons.append(
                    "Spread is excellent for intraday execution."
                )

            elif spread <= 0.25:

                liquidity_score = 8

                reasons.append(
                    "Spread is acceptable for intraday execution."
                )

            elif spread <= 0.50:

                liquidity_score = 6

                reasons.append(
                    "Spread is moderate."
                )

            elif spread <= 1.00:

                liquidity_score = 3

                reasons.append(
                    "Spread is relatively wide."
                )

                warnings.append(
                    "Wide spread may reduce realised profit."
                )

            else:

                liquidity_score = 0

                reasons.append(
                    "Spread is too wide for a preferred "
                    "intraday trade."
                )

                warnings.append(
                    "Poor liquidity creates execution risk."
                )

        except (
            ValueError,
            TypeError
        ):

            liquidity_score = 0

            warnings.append(
                "Spread data could not be evaluated."
            )

    # -----------------------------------------
    # 6. EXHAUSTION PENALTY — UP TO -15
    # -----------------------------------------

    exhaustion_penalty = 0

    # V0.2 exhaustion is based on the quality of
    # the move, not simply the size of the move.

    # -----------------------------------------
    # 6A. ACCELERATION SLOWDOWN — UP TO -4
    # -----------------------------------------

    acceleration_penalty = 0

    if acceleration_change < 0:

        slowdown_base = abs(acceleration_change)

        if slowdown_base >= 0.25:

            acceleration_penalty = -4

        elif slowdown_base >= 0.10:

            acceleration_penalty = -3

        else:

            acceleration_penalty = -2

    # -----------------------------------------
    # 6B. VOLUME DETERIORATION — UP TO -3
    # -----------------------------------------

    volume_penalty = 0

    if volume_change < 0:

        volume_drop = abs(volume_change)

        if volume_drop > 35:

            volume_penalty = -3

        elif volume_drop >= 20:

            volume_penalty = -2

        elif volume_drop >= 10:

            volume_penalty = -1

    # -----------------------------------------
    # 6C. STRUCTURE DETERIORATION — UP TO -3
    # -----------------------------------------

    structure_penalty = 0

    if higher_highs < 2 and higher_lows < 2:

        structure_penalty = -3

    elif higher_highs < 3 or higher_lows < 3:

        structure_penalty = -1

    # -----------------------------------------
    # 6D. EXCESSIVE EXTENSION — UP TO -2
    # -----------------------------------------

    extension_penalty = 0

    if price_change >= 2.0:

        extension_penalty = -2

    elif price_change >= 1.25:

        extension_penalty = -1

    # -----------------------------------------
    # 6E. UNDERLYING DETERIORATION — UP TO -3
    # -----------------------------------------

    underlying_penalty = 0

    if underlying_history is not None:

        if "underlying_change" in locals():

            if underlying_change < -0.50:

                underlying_penalty = -3

            elif underlying_change < -0.25:

                underlying_penalty = -2

            elif underlying_change < 0:

                underlying_penalty = -1

    # -----------------------------------------
    # TOTAL EXHAUSTION PENALTY
    # -----------------------------------------

    exhaustion_penalty = (
        acceleration_penalty
        + volume_penalty
        + structure_penalty
        + extension_penalty
        + underlying_penalty
    )

    exhaustion_penalty = max(
        -15,
        min(exhaustion_penalty, 0)
    )

    if exhaustion_penalty == 0:

        reasons.append(
            "No significant exhaustion penalty detected."
        )

    elif exhaustion_penalty >= -4:

        reasons.append(
            "Early signs of exhaustion are present."
        )

        warnings.append(
            "Monitor acceleration, volume and structure "
            "before entering."
        )

    elif exhaustion_penalty >= -9:

        reasons.append(
            "Multiple exhaustion warning signals are present."
        )

        warnings.append(
            "Momentum quality is weakening; avoid chasing."
        )

    else:

        reasons.append(
            "Strong exhaustion or reversal risk is detected."
        )

        warnings.append(
            "Severe exhaustion detected: no new entry."
        )
    # -----------------------------------------
    # 7. REMAINING PROFIT POTENTIAL — 10 POINTS
    # -----------------------------------------

    if remaining_profit_percentage is None:

        profit_potential_score = 5

        reasons.append(
            "Remaining profit potential has not yet "
            "been estimated; partial score credited."
        )

        warnings.append(
            "Profit potential must be evaluated before entry."
        )

    else:

        try:

            remaining_profit = float(
                remaining_profit_percentage
            )

            if remaining_profit <= 0:

                profit_potential_score = 0

                reasons.append(
                    "Insufficient remaining profit potential."
                )

            elif remaining_profit < 0.50:

                profit_potential_score = 3

                reasons.append(
                    "Remaining profit potential is limited."
                )

            elif remaining_profit < 1.00:

                profit_potential_score = 6

                reasons.append(
                    "Remaining profit potential is acceptable."
                )

            elif remaining_profit < 2.00:

                profit_potential_score = 8

                reasons.append(
                    "Remaining profit potential is attractive."
                )

            else:

                profit_potential_score = 10

                reasons.append(
                    "Remaining profit potential is strong."
                )

        except (
            ValueError,
            TypeError
        ):

            profit_potential_score = 0

            warnings.append(
                "Remaining profit potential could not "
                "be evaluated."
            )

    # -----------------------------------------
    # 8. RISK / REWARD — 10 POINTS
    # -----------------------------------------

    if risk_reward_ratio is None:

        risk_reward_score = 5

        reasons.append(
            "Risk/reward information is unavailable; "
            "partial score credited."
        )

        warnings.append(
            "Risk/reward must be confirmed before entry."
        )

    else:

        try:

            rr = float(
                risk_reward_ratio
            )

            if rr < 1.0:

                risk_reward_score = 0

                reasons.append(
                    "Risk/reward is unacceptable."
                )

            elif rr < 1.5:

                risk_reward_score = 3

                reasons.append(
                    "Risk/reward is weak."
                )

            elif rr < 2.0:

                risk_reward_score = 6

                reasons.append(
                    "Risk/reward is acceptable."
                )

            elif rr < 2.5:

                risk_reward_score = 8

                reasons.append(
                    "Risk/reward is strong."
                )

            else:

                risk_reward_score = 10

                reasons.append(
                    "Risk/reward is excellent."
                )

        except (
            ValueError,
            TypeError
        ):

            risk_reward_score = 0

            warnings.append(
                "Risk/reward data could not be evaluated."
            )

    # -----------------------------------------
    # FINAL SCORE
    # -----------------------------------------

    score = (
        price_score
        + volume_score
        + underlying_score
        + structure_score
        + liquidity_score
        + exhaustion_penalty
        + profit_potential_score
        + risk_reward_score
    )

    score = max(
        0,
        min(score, 100)
    )

    # -----------------------------------------
    # HARD SAFETY OVERRIDES
    # -----------------------------------------

    hard_no_trade = False

    if liquidity_score == 0:

        hard_no_trade = True

        warnings.append(
            "Hard safety override: liquidity/spread "
            "is unacceptable."
        )

    if (
        remaining_profit_percentage is not None
        and profit_potential_score == 0
    ):

        hard_no_trade = True

        warnings.append(
            "Hard safety override: insufficient "
            "remaining profit potential."
        )

    if (
        risk_reward_ratio is not None
        and risk_reward_score == 0
    ):

        hard_no_trade = True

        warnings.append(
            "Hard safety override: unacceptable "
            "risk/reward."
        )

    if hard_no_trade:

        status = "NO TRADE"
        strength = "WEAK"
        trade_candidate = False

    elif score >= 80:

        status = "STRONG MOMENTUM"
        strength = "STRONG"
        trade_candidate = True

    elif score >= 65:

        status = "DEVELOPING"
        strength = "MODERATE"
        trade_candidate = False

    else:

        status = "NO TRADE"
        strength = "WEAK"
        trade_candidate = False

    # -----------------------------------------
    # FINAL RESULT
    # -----------------------------------------

    return {
        "Momentum Status":
            status,

        "Momentum Strength":
            strength,

        "Momentum Score":
            score,

        "Trade Candidate":
            trade_candidate,

        "Price Acceleration Score":
            price_score,

        "Volume Acceleration Score":
            volume_score,

        "Underlying Confirmation Score":
            underlying_score,

        "Structure Score":
            structure_score,

        "Liquidity Score":
            liquidity_score,

        "Exhaustion Penalty":
            exhaustion_penalty,

        "Remaining Profit Potential Score":
            profit_potential_score,

        "Risk Reward Score":
            risk_reward_score,

        "Price Change Percentage":
            round(price_change, 2),

        "Volume Change Percentage":
            round(volume_change, 2),

        "Reasons":
            reasons,

        "Warnings":
            warnings
    }
