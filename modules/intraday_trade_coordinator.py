"""
JKJ AI Intraday Trade Coordinator v0.1

Wisdom Before Wealth.

This module coordinates the complete intraday
decision process.

Flow:

1. Analyse the intraday market.
2. Analyse the stock setup.
3. Analyse trade risk.
4. Produce a final trading decision.

No broker connection or real order execution
is performed here.
"""


from intraday_market_engine import (
    analyse_intraday_market
)

from intraday_setup_engine import (
    analyse_intraday_setup
)

from intraday_risk_engine import (
    analyse_intraday_risk
)

from intraday_decision_engine import (
    make_intraday_decision
)


def analyse_intraday_trade(

    market_price,
    market_ma20,
    market_ma50,
    market_rsi,

    stock_price,
    stock_ma20,
    stock_rsi,
    short_term_trend,
    volume_trend,

    entry_price,
    stop_loss,
    target_price
):
    """
    Run the complete JKJ intraday analysis.

    Returns the results from:

    - Market Engine
    - Setup Engine
    - Risk Engine
    - Decision Engine
    """

    # -----------------------------------------
    # STEP 1 — MARKET ANALYSIS
    # -----------------------------------------

    market_data = {

        "Current Price":
            market_price,

        "MA20":
            market_ma20,

        "MA50":
            market_ma50,

        "RSI":
            market_rsi
    }


    market_result = analyse_intraday_market(
        market_data
    )

    # -----------------------------------------
    # STEP 2 — STOCK SETUP ANALYSIS
    # -----------------------------------------

    stock_data = {

        "Current Price":
            stock_price,

        "MA20":
            stock_ma20,

        "RSI":
            stock_rsi,

        "Volume Trend":
            volume_trend,

        "Short-Term Trend":
            short_term_trend
    }


    setup_result = analyse_intraday_setup(
        stock_data
    )

    # -----------------------------------------
    # STEP 3 — RISK ANALYSIS
    # -----------------------------------------

    risk_result = analyse_intraday_risk(

        entry_price=entry_price,

        stop_loss=stop_loss,

        target_price=target_price,

        setup_score=setup_result.get(
            "Setup Score",
            0
        ),

        trading_allowed=market_result.get(
            "Trading Allowed",
            False
        )
    )

    # -----------------------------------------
    # STEP 4 — FINAL DECISION
    # -----------------------------------------

    decision_result = make_intraday_decision(

        market_result,

        setup_result,

        risk_result
    )

    # -----------------------------------------
    # COMPLETE RESULT
    # -----------------------------------------

    return {

        "Market Analysis":
            market_result,

        "Setup Analysis":
            setup_result,

        "Risk Analysis":
            risk_result,

        "Final Decision":
            decision_result
    }