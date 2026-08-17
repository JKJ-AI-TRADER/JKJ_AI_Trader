import streamlit as st
from modules.settings import APP_NAME, APP_VERSION, PHILOSOPHY
from modules.database import create_database, save_profile, get_profile
from modules.portfolio import show
from modules.opportunity_engine import calculate_opportunity_score
from modules.stock_data import get_stock_data
from modules.technical_engine import calculate_technical_quality
from modules.volume_engine import calculate_volume_confirmation
from modules.market_engine import calculate_market_alignment
from modules.sector_engine import calculate_sector_strength
from modules.decision_engine import generate_decision

st.set_page_config(page_title=APP_NAME, page_icon="📈", layout="wide")

create_database()

st.header(f"{APP_NAME} {APP_VERSION}")
st.caption(PHILOSOPHY)

st.caption("A disciplined investment decision support platform focused on capital protection.")

existing = get_profile()
st.divider()

st.subheader("Opportunity Intelligence Engine")

stock_symbol = st.text_input(
    "Enter Stock Symbol",
    "KITEX"
)

if st.button("Analyse Stock"):

    st.write(f"Analysing: {stock_symbol}")

    
    stock = get_stock_data(stock_symbol)

    st.write(stock)
stock = get_stock_data(stock_symbol)

st.write(stock)

# JKJ AI Opportunity Score v0.1
technical_result = calculate_technical_quality(stock)

volume_result = calculate_volume_confirmation(stock)

market_result = calculate_market_alignment(stock)

sector_result = calculate_sector_strength(stock)

score = calculate_opportunity_score(
    market_alignment=market_result["Market Alignment Score"],
    sector_strength=sector_result["Sector Strength Score"],
    technical_quality=technical_result["Technical Quality Score"],
    volume_confirmation=volume_result["Volume Confirmation Score"],
    risk_reward=17
)

st.subheader("Opportunity Intelligence Score")

st.write(f"Overall Score: {score['Overall Score']}/100")
decision = generate_decision(
    opportunity_score=score["Overall Score"],
    risk_level="HIGH",
    portfolio_loss=-42.45
)

st.subheader("JKJ AI Decision")

st.write(decision["JKJ Decision"])

for reason in decision["Reasons"]:
    st.write("• " + reason)

st.write("Score Explanation:")
st.write("Technical Analysis:")
for item in technical_result["Technical Explanation"]:
    st.write("•", item)
st.write("Market Analysis:")

for item in market_result["Market Explanation"]:
    st.write("•", item)    
for item in score["Explanation"]:
    st.write("•", item)
st.write("Volume Analysis:")

for item in volume_result["Volume Explanation"]:
    st.write("•", item)
st.subheader("Investor Profile")


default_name = existing[1] if existing else "Johny"
default_capital = existing[2] if existing else 50000
default_risk = existing[3] if existing else "Moderate"
default_intraday = existing[4] if existing else 20

name = st.text_input("Investor Name", default_name)
capital = st.number_input(
    "Available Capital (₹)",
    min_value=0.0,
   value=float(default_capital)
)
risk = st.selectbox("Risk Preference", ["Conservative", "Moderate", "Aggressive"],
                    index=["Conservative", "Moderate", "Aggressive"].index(default_risk))
intraday = st.slider("Intraday Allocation %", 0, 100, int(default_intraday))
investment = 100 - intraday

st.write(f"Investment Allocation: {investment}%")
st.write(f"Intraday Allocation: {intraday}%")



if st.button("Save Profile"):
    save_profile(name, capital, risk, intraday, investment)
    st.success("Investor profile saved successfully")


show()
    


