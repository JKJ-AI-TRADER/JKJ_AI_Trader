import streamlit as st
from modules.settings import APP_NAME, VERSION, PHILOSOPHY
from modules.database import create_database, save_profile, get_profile

st.set_page_config(page_title=APP_NAME, page_icon="📈", layout="wide")

create_database()

st.title(f"{APP_NAME} {VERSION}")
st.subheader(PHILOSOPHY)

st.write("A disciplined investment decision support platform focused on capital protection.")

existing = get_profile()

st.header("Investor Profile")

default_name = existing[1] if existing else "Johny"
default_capital = existing[2] if existing else 50000
default_risk = existing[3] if existing else "Moderate"
default_intraday = existing[4] if existing else 20

name = st.text_input("Investor Name", default_name)
capital = st.number_input("Available Capital (₹)", min_value=0, value=float(default_capital))
risk = st.selectbox("Risk Preference", ["Conservative", "Moderate", "Aggressive"],
                    index=["Conservative", "Moderate", "Aggressive"].index(default_risk))
intraday = st.slider("Intraday Allocation %", 0, 100, int(default_intraday))
investment = 100 - intraday

st.write(f"Investment Allocation: {investment}%")
st.write(f"Intraday Allocation: {intraday}%")

if st.button("Save Profile"):
    save_profile(name, capital, risk, intraday, investment)
    st.success("Investor profile saved successfully")

st.divider()
st.success("JKJ AI Trader Foundation Running")
