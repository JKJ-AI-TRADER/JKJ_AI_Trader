"""
JKJ AI Stock Scanner v0.4

Wisdom Before Wealth.

This engine scans a list of stocks using the existing
JKJ AI analysis system, ranks them by opportunity score,
and preserves the key analysis results for explanation.
"""

from modules.analysis_engine import analyze_stock


def scan_stocks(stock_list):
    """
    Analyse a list of stocks and rank them by
    Combined Opportunity Score.
    """

    results = []

    print()
    print()

    # -----------------------------------------
    # SCAN EACH STOCK
    # -----------------------------------------

    for symbol in stock_list:

        print(f"Scanning {symbol}...")

        try:

            # -----------------------------------------
            # RUN COMPLETE ANALYSIS
            # -----------------------------------------

            analysis = analyze_stock(symbol)

            if analysis.get(
                "Analysis Status"
            ) != "COMPLETE":

                print(
                    f"Unable to analyse {symbol}."
                )

                continue

            # -----------------------------------------
            # SCORE ANALYSIS
            # -----------------------------------------

            score_analysis = analysis.get(
                "Score Analysis",
                {}
            )

            combined_score = score_analysis.get(
                "Combined Opportunity Score",
                0
            )

            # -----------------------------------------
            # MARKET ANALYSIS
            # -----------------------------------------

            market_analysis = analysis.get(
                "Market Analysis",
                {}
            )

            market_condition = market_analysis.get(
                "Market Condition",
                market_analysis.get(
                    "Market State",
                    "UNKNOWN"
                )
            )

            market_score = market_analysis.get(
                "Standard Score",
                0
            )

            # -----------------------------------------
            # MARKET CONFIRMATION
            # -----------------------------------------

            market_confirmation = analysis.get(
                "Market Confirmation",
                {}
            )

            market_confirmation_status = (
                market_confirmation.get(
                    "Market Confirmation Status",
                    "UNKNOWN"
                )
            )

            market_strength = market_confirmation.get(
                "Market Strength",
                "UNKNOWN"
            )

            recovery_stage = market_confirmation.get(
                "Recovery Stage",
                "UNKNOWN"
            )

            buying_environment = market_confirmation.get(
                "Buying Environment",
                "UNKNOWN"
            )

            buying_allowed = market_confirmation.get(
                "Buying Allowed",
                False
            )

            market_message = market_confirmation.get(
                "Market Message",
                "No market confirmation message available."
            )

            # -----------------------------------------
            # TECHNICAL ANALYSIS
            # -----------------------------------------

            technical_analysis = analysis.get(
                "Technical Analysis",
                {}
            )

            technical_condition = technical_analysis.get(
                "Technical Condition",
                "UNKNOWN"
            )

            technical_score = technical_analysis.get(
                "Standard Score",
                0
            )

            # -----------------------------------------
            # MOMENTUM ANALYSIS
            # -----------------------------------------

            momentum_analysis = analysis.get(
                "Momentum Analysis",
                {}
            )

            momentum_condition = momentum_analysis.get(
                "Momentum Condition",
                "UNKNOWN"
            )

            momentum_score = momentum_analysis.get(
                "Standard Score",
                0
            )

            # -----------------------------------------
            # OPPORTUNITY ANALYSIS
            # -----------------------------------------

            opportunity_analysis = analysis.get(
                "Opportunity Analysis",
                {}
            )

            opportunity_condition = opportunity_analysis.get(
                "Opportunity Condition",
                "UNKNOWN"
            )

            opportunity_score = opportunity_analysis.get(
                "Standard Score",
                0
            )

            # -----------------------------------------
            # STOCK STRENGTH
            # -----------------------------------------

            stock_strength_score = (
                technical_score
                + momentum_score
                + opportunity_score
            ) / 3

            stock_strength_score = round(
                stock_strength_score,
                2
            )

            # -----------------------------------------
            # RISK ANALYSIS
            # -----------------------------------------

            risk_analysis = analysis.get(
                "Risk Analysis",
                {}
            )

            risk_level = risk_analysis.get(
                "Risk Level",
                "UNKNOWN"
            )

            # -----------------------------------------
            # FINAL DECISION
            # -----------------------------------------

            decision = analysis.get(
                "Final Decision",
                {}
            ).get(
                "JKJ Decision",
                "UNKNOWN"
            )

            # -----------------------------------------
            # WATCH REASON
            # -----------------------------------------

            if decision == "WAIT FOR MARKET CONFIRMATION":

                watch_reason = (
                    "Strong setup waiting for "
                    "market confirmation"
                )

            elif technical_score >= 60:

                watch_reason = (
                    "Technical setup is improving"
                )

            elif momentum_score >= 60:

                watch_reason = (
                    "Momentum is building"
                )

            else:

                watch_reason = (
                    "Conditions are still developing"
                )

            # -----------------------------------------
            # BUY TRIGGER DATA
            # -----------------------------------------

            stock_data = analysis.get(
                "Stock Data",
                {}
            )

            current_price = stock_data.get(
                "Current Price",
                0
            )

            ma20 = stock_data.get(
                "MA20",
                0
            )

            ma50 = stock_data.get(
                "MA50",
                0
            )

            rsi = stock_data.get(
                "RSI",
                0
            )

            # -----------------------------------------
            # PRICE STATUS
            # -----------------------------------------

            if (
                current_price > 0
                and ma20 > 0
                and ma50 > 0
            ):

                if (
                    current_price >= ma20
                    and current_price >= ma50
                ):

                    price_status = (
                        "Price above MA20 and MA50"
                    )

                elif current_price >= ma20:

                    price_status = (
                        "Price above MA20 but below MA50"
                    )

                elif current_price >= ma50:

                    price_status = (
                        "Price above MA50 but below MA20"
                    )

                else:

                    price_status = (
                        "Price below MA20 and MA50"
                    )

            else:

                price_status = (
                    "Price data unavailable"
                )

            # -----------------------------------------
            # BUY TRIGGER v0.4
            # -----------------------------------------

            trigger_conditions = []

            # -----------------------------------------
            # MARKET CONFIRMATION
            # -----------------------------------------

            if market_condition == "Bearish":

                trigger_conditions.append(
                    "Market must improve from Bearish "
                    "to Recovering or Bullish"
                )

            elif market_condition == "Recovering":

                trigger_conditions.append(
                    "Market recovery must be confirmed"
                )

            # -----------------------------------------
            # PRICE VS MA20
            # -----------------------------------------

            if (
                ma20 > 0
                and current_price < ma20
            ):

                trigger_conditions.append(
                    "Price must move above MA20"
                )

            # -----------------------------------------
            # PRICE VS MA50
            # -----------------------------------------

            if (
                ma50 > 0
                and current_price < ma50
            ):

                trigger_conditions.append(
                    "Price must move above MA50"
                )

            # -----------------------------------------
            # RSI CONFIRMATION
            # -----------------------------------------

            if (
                rsi > 0
                and rsi < 55
            ):

                trigger_conditions.append(
                    "RSI must improve to 55 or above"
                )

            # -----------------------------------------
            # TECHNICAL CONFIRMATION
            # -----------------------------------------

            if technical_score < 60:

                trigger_conditions.append(
                    "Technical score must improve to "
                    "60 or above"
                )

            # -----------------------------------------
            # MOMENTUM CONFIRMATION
            # -----------------------------------------

            if momentum_score < 60:

                trigger_conditions.append(
                    "Momentum score must improve to "
                    "60 or above"
                )

            # -----------------------------------------
            # OPPORTUNITY CONFIRMATION
            # -----------------------------------------

            if opportunity_score < 60:

                trigger_conditions.append(
                    "Opportunity score must improve to "
                    "60 or above"
                )

            # -----------------------------------------
            # FINAL BUY TRIGGER
            # -----------------------------------------

            if (
                buying_allowed
                and not trigger_conditions
            ):

                buy_trigger = (
                    "BUY CONDITIONS CONFIRMED"
                )

            elif trigger_conditions:

                buy_trigger = " | ".join(
                    trigger_conditions
                )

            else:

                buy_trigger = (
                    "Wait for overall buying conditions "
                    "to improve"
                )

            # -----------------------------------------
            # JKJ FINAL ACTION CLASSIFICATION
            # -----------------------------------------

            if (
                buying_allowed
                and stock_strength_score >= 70
                and technical_score >= 70
                and momentum_score >= 60
                and opportunity_score >= 60
                and risk_level == "Low"
                and not trigger_conditions
            ):

                final_action = "BUY NOW"

            elif (
                stock_strength_score >= 60
                and risk_level != "High"
            ):

                final_action = "WATCH FOR BUY"

            elif (
                technical_score >= 70
                and combined_score >= 40
                and risk_level == "Low"
            ):

                final_action = "WATCH FOR BUY"

            elif combined_score >= 30:

                final_action = "WAIT"

            else:

                final_action = "AVOID / NO TRADE"

            # -----------------------------------------
            # SAVE SCANNER RESULT
            # -----------------------------------------

            results.append(
                {
                    "Symbol": symbol,
                    "Score": combined_score,
                    "Risk": risk_level,
                    "Decision": decision,
                    "Watch Reason": watch_reason,
                    "Buy Trigger": buy_trigger,
                    "Final Action": final_action,

                    "Current Price": current_price,
                    "MA20": ma20,
                    "MA50": ma50,
                    "RSI": rsi,
                    "Price Status": price_status,

                    "Market Condition": market_condition,
                    "Market Score": market_score,

                    "Technical Condition": (
                        technical_condition
                    ),

                    "Technical Score": technical_score,

                    "Momentum Condition": (
                        momentum_condition
                    ),

                    "Momentum Score": momentum_score,

                    "Opportunity Condition": (
                        opportunity_condition
                    ),

                    "Opportunity Score": opportunity_score,

                    "Market Confirmation Status": (
                        market_confirmation_status
                    ),

                    "Market Strength": market_strength,

                    "Recovery Stage": recovery_stage,

                    "Buying Environment": (
                        buying_environment
                    ),

                    "Buying Allowed": buying_allowed,

                    "Market Message": market_message,

                    "Stock Strength Score": (
                        stock_strength_score
                    )
                }
            )

        except Exception as error:

            print(
                f"Error analysing {symbol}: {error}"
            )

        # -----------------------------------------
    # SORT BEST SCORE FIRST
    # -----------------------------------------

    results.sort(
        key=lambda item: item["Score"],
        reverse=True
    )

    # -----------------------------------------
    # GROUP STOCKS BY FINAL ACTION
    # -----------------------------------------

    buy_now_stocks = [
        stock for stock in results
        if stock.get("Final Action") == "BUY NOW"
    ]

    watch_for_buy_stocks = [
        stock for stock in results
        if stock.get("Final Action") == "WATCH FOR BUY"
    ]

    wait_stocks = [
        stock for stock in results
        if stock.get("Final Action") == "WAIT"
    ]

    avoid_stocks = [
        stock for stock in results
        if stock.get("Final Action") == "AVOID / NO TRADE"
    ]

    # -----------------------------------------
    # RETURN ALL RESULTS
    # -----------------------------------------

    return results