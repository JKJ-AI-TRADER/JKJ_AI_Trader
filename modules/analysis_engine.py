"""
JKJ AI Analysis Engine v0.2

Wisdom Before Wealth.

This is the master coordinator for JKJ AI Trader.

It brings together:
- Stock Data
- Market Analysis
- Technical Analysis
- Opportunity Analysis
- Combined Opportunity Score
- Risk Analysis
- Trend Analysis
- Recovery Confirmation
- JKJ Decision

The engine does not place trades.
It produces an explainable analysis.
"""

from modules.stock_data import get_stock_data
from modules.market_engine import analyze_market
from modules.technical_engine import analyze_technical
from modules.opportunity_engine import analyze_opportunity
from modules.score_engine import calculate_combined_score
from modules.risk_engine import analyze_risk
from modules.decision_engine import generate_decision
from modules.holding_decision_engine import analyze_holding


def analyze_stock(
    symbol,
    portfolio_loss=0,
    holding_status=False,
    stock_loss=0,
    trend="UNKNOWN",
    long_term_trend="UNKNOWN",
    recovery_confirmed=False
):
    """
    Run the complete JKJ AI Trader analysis
    for a single stock.

    Existing holdings and new investment
    opportunities use separate decision engines.
    """
    # -----------------------------------------
    # 1. GET MARKET DATA
    # -----------------------------------------

    stock_data = get_stock_data(symbol)

    if stock_data.get("Data Status") != "COMPLETE":
        return {
            "Symbol": symbol,
            "Analysis Status": "FAILED",
            "Reason": stock_data.get(
                "Status",
                "Unable to retrieve stock data."
            )
        }

    # -----------------------------------------
    # TREND INFORMATION FROM STOCK DATA
    # -----------------------------------------

    short_term_trend = stock_data.get(
        "Short-Term Trend",
        "UNKNOWN"
    )

    long_term_trend = stock_data.get(
        "Long-Term Trend",
        "UNKNOWN"
    )

    recovery_confirmed = stock_data.get(
        "Recovery Confirmed",
        False
    )

    

    # -----------------------------------------
    # 2. MARKET ANALYSIS
    # -----------------------------------------

    market_result = analyze_market(
        stock_data.get("Market Data", {})
    )

    # -----------------------------------------
    # 3. TECHNICAL ANALYSIS
    # -----------------------------------------

    technical_result = analyze_technical(
        stock_data
    )

    # -----------------------------------------
    # 4. OPPORTUNITY ANALYSIS
    # -----------------------------------------

    opportunity_result = analyze_opportunity(
        stock_data
    )

    # -----------------------------------------
    # 5. COMBINED OPPORTUNITY SCORE
    # -----------------------------------------

    score_result = calculate_combined_score(
        market_result,
        technical_result,
        opportunity_result
    )

    combined_score = score_result.get(
        "Combined Opportunity Score",
        0
    )

    # -----------------------------------------
    # 6. RISK ANALYSIS
    # -----------------------------------------

    risk_result = analyze_risk(
        stock_data
    )

    risk_level = risk_result.get(
        "Risk Level",
        "HIGH"
    )

    # -----------------------------------------
    # 7. FINAL JKJ DECISION
    # -----------------------------------------

    if holding_status:

        decision_result = analyze_holding(
            stock_name=symbol.upper(),
            stock_loss=stock_loss,
            opportunity_score=combined_score,
            risk_level=risk_level,
            trend=short_term_trend,
            long_term_trend=long_term_trend,
            recovery_confirmed=recovery_confirmed
        )

    else:

        decision_result = generate_decision(
            opportunity_score=combined_score,
            risk_level=risk_level,
            portfolio_loss=portfolio_loss,
            holding_status=False,
            trend=short_term_trend,
            long_term_trend=long_term_trend,
            recovery_confirmed=recovery_confirmed
        )

    # -----------------------------------------
    # FINAL EXPLAINABLE RESULT
    # -----------------------------------------

    return {
        "Symbol": symbol.upper(),
        "Analysis Status": "COMPLETE",

        "Holding Status": holding_status,

        "Stock Data": stock_data,

        "Market Analysis": market_result,
        "Technical Analysis": technical_result,
        "Opportunity Analysis": opportunity_result,

        "Score Analysis": score_result,

        "Risk Analysis": risk_result,

"Short-Term Trend": short_term_trend,
        "Long-Term Trend": long_term_trend,
        "Recovery Confirmed": recovery_confirmed,

        "Final Decision": decision_result
    }