import streamlit as st
from datetime import date
from database import create_database, add_holding, get_portfolio
from modules.stock_data import get_stock_data
from modules.risk_guardian import calculate_stock_risk
from modules.portfolio_engine import calculate_portfolio
def show():
    # Initialize database
    create_database()
    
st.write("")

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

        add_holding(
        stock_name,
        quantity,
        buy_price,
        current_price,
        str(buy_date)
    )

st.toast("Stock holding saved successfully")    
st.markdown("---")
# ==============================
# JKJ AI Portfolio Health v0.2
# ==============================

portfolio = get_portfolio()

if portfolio:

    total_investment = 0
    total_current_value = 0

    for item in portfolio:
        stock = item[0]
        quantity = item[1]
        buy_price = item[2]

        live_data = get_stock_data(stock)

        current_price = live_data.get(
            "Current Price",
            item[3]
        )

        total_investment += quantity * buy_price
        total_current_value += quantity * current_price
        total_profit_loss = total_current_value - total_investment
        total_return = (total_profit_loss / total_investment) * 100
  

    if total_investment > 0:
        portfolio_return = (
            total_profit_loss / total_investment
        ) * 100
    else:
        portfolio_return = 0


    st.subheader("📊 JKJ AI Portfolio Health")

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


if total_return <= -20:

    st.error(
        f"🚨 Capital Protection Alert\n\n"
        f"Portfolio drawdown has exceeded the JKJ AI safety limit.\n\n"
        f"Current Loss: {round(total_return,2)}%\n\n"
        "Action:\n"
        "Review holdings. Protect capital before attempting recovery."
    )

elif total_return <= -10:

    st.warning(
        "🔴 Risk Alert: Portfolio loss exceeds 10%. "
        "Review holdings and protect capital."
    )

elif total_return <= -5:

    st.info(
        "🟡 Caution: Portfolio showing weakness. "
        "Monitor closely before adding exposure."
    )

else:

    st.success(
        "🟢 Portfolio health is within acceptable risk limits."
    )

st.markdown("---")
portfolio = get_portfolio()   
st.subheader("My Portfolio Holdings")
if st.button("🔄 Refresh Live Prices"):
    st.rerun()



if portfolio:

    st.write("")

data = []

for item in portfolio:

    stock = item[0]
    quantity = item[1]
    buy_price = item[2]
    buy_date = item[4]

    live_data = get_stock_data(stock)

    current_price = live_data.get(
        "Current Price",
        item[3]
    )

    investment = quantity * buy_price
    current_value = quantity * current_price
    profit_loss = current_value - investment

    if investment > 0:
        return_percent = (profit_loss / investment) * 100
    else:
        return_percent = 0

    data.append({
        "Stock": stock,
        "Quantity": quantity,
        "Buy Price": buy_price,
        "Current Price": current_price,
        "Investment": investment,
        "Current Value": current_value,
        "Profit/Loss": profit_loss,
        "Return %": round(return_percent, 2),
        "Buy Date": buy_date
    })

    st.table(data)


