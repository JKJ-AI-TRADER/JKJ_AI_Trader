import streamlit as st
from datetime import date

from modules.portfolio_engine import calculate_portfolio
from database import (
    create_database,
    add_holding,
    get_portfolio
)

from modules.stock_data import get_stock_data



def show():

    # ==========================================
    # Initialize Database
    # ==========================================

    create_database()

    st.write("")

    # ==========================================
    # Add New Portfolio Holding
    # ==========================================

    st.markdown("### Add New Portfolio Holding")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        stock_name = st.text_input("Stock")

    with col2:
        quantity = st.number_input(
            "Qty",
            min_value=1,
            value=1
        )

    with col3:
        buy_price = st.number_input(
            "Buy Price",
            min_value=0.0,
            value=0.0
        )

    with col4:
        current_price = st.number_input(
            "Current Price",
            min_value=0.0,
            value=0.0
        )

    with col5:
        buy_date = st.date_input(
            "Buy Date",
            date.today()
        )

    if st.button("Save Holding"):

        if not stock_name.strip():
            st.warning("Please enter a stock name.")

        elif buy_price <= 0:
            st.warning("Please enter a valid Buy Price.")

        else:

            add_holding(
                stock_name.strip().upper(),
                quantity,
                buy_price,
                current_price,
                str(buy_date)
            )

            st.success("Stock holding saved successfully.")
            st.rerun()

    st.markdown("---")

    # ==========================================
    # Load Portfolio
    # ==========================================

    portfolio = get_portfolio()

    # ==========================================
    # Prepare Live Portfolio Data
    # ==========================================

    holdings_for_engine = []

    for item in portfolio:

        stock = item[0]
        quantity = item[1]
        buy_price = item[2]
        stored_current_price = item[3]
        buy_date = item[4]

        live_data = get_stock_data(stock)

        current_price = live_data.get("Current Price")

        if current_price is None:
            current_price = stored_current_price

        holdings_for_engine.append(
            (
                stock,
                quantity,
                buy_price,
                current_price,
                buy_date
            )
        )
    # ==========================================
    # Portfolio Engine
    # ==========================================

    portfolio_result = calculate_portfolio(
        holdings_for_engine
    )

    # ==========================================
    # JKJ AI Portfolio Health
    # ==========================================

    st.subheader("📊 JKJ AI Portfolio Health")

    total_investment = portfolio_result[
        "total_investment"
    ]

    total_current_value = portfolio_result[
        "total_current_value"
    ]

    total_profit_loss = portfolio_result[
        "total_profit_loss"
    ]

    portfolio_return = portfolio_result[
        "portfolio_return"
    ]

    number_of_holdings = portfolio_result[
        "number_of_holdings"
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Investment",
            f"₹{total_investment:,.0f}"
        )

    with col2:
        st.metric(
            "Current Value",
            f"₹{total_current_value:,.0f}"
        )

    with col3:
        st.metric(
            "Profit / Loss",
            f"₹{total_profit_loss:,.0f}"
        )

    with col4:
        st.metric(
            "Return %",
            f"{portfolio_return:.2f}%"
        )

    # ==========================================
    # JKJ Capital Protection Alerts
    # ==========================================

    if portfolio_return <= -20:

        st.error(
            "🚨 Capital Protection Alert\n\n"
            "Portfolio drawdown has exceeded "
            "the JKJ AI safety limit.\n\n"
            f"Current Loss: {portfolio_return:.2f}%\n\n"
            "Action:\n"
            "Review holdings. Protect capital "
            "before attempting recovery."
        )

    elif portfolio_return <= -10:

        st.warning(
            "🔴 Risk Alert: Portfolio loss exceeds 10%. "
            "Review holdings and protect capital."
        )

    elif portfolio_return <= -5:

        st.info(
            "🟡 Caution: Portfolio showing weakness. "
            "Monitor closely before adding exposure."
        )

    else:

        st.success(
            "🟢 Portfolio health is within acceptable "
            "risk limits."
        )

    st.markdown("---")

    # ==========================================
    # Portfolio Holdings
    # ==========================================

    st.subheader("My Portfolio Holdings")

    if st.button("🔄 Refresh Live Prices"):
        st.rerun()

    if not portfolio_result["holdings"]:

        st.info(
            "No portfolio holdings yet. "
            "Add your first holding above."
        )

        return

    # ==========================================
    # Holdings Table
    # ==========================================

    data = []

    for holding in portfolio_result["holdings"]:

        data.append(
            {
                "Stock": holding["Stock"],
                "Quantity": holding["Quantity"],
                "Buy Price": holding["Buy Price"],
                "Current Price": holding["Current Price"],
                "Investment": holding["Investment"],
                "Current Value": holding["Current Value"],
                "Profit/Loss": holding["Profit/Loss"],
                "Return %": round(
                    holding["Return %"],
                    2
                ),
                "Allocation %": round(
                    holding["Allocation %"],
                    2
                ),
                "Buy Date": holding["Buy Date"]
            }
        )

    st.table(data)

    st.caption(
        f"JKJ AI Portfolio Engine | "
        f"{number_of_holdings} holding(s)"
    )
