import sqlite3
from pathlib import Path
from modules.opportunity_engine import calculate_opportunity_score
DATABASE = "database/jkj_ai.db"

def create_database():
    Path("database").mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investor_profile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        capital REAL,
        risk_level TEXT,
        intraday_percentage INTEGER,
        investment_percentage INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_holdings (
        id INTEGER PRIMARY KEY,
        stock_name TEXT,
        quantity INTEGER,
        buy_price REAL,
        current_price REAL,
        buy_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_profile(name, capital, risk, intraday, investment):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investor_profile")
    cursor.execute("""
    INSERT INTO investor_profile
    VALUES (1,?,?,?,?,?)
    """, (name, capital, risk, intraday, investment))
    conn.commit()
    conn.close()

def get_profile():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM investor_profile")
    data = cursor.fetchone()
    conn.close()
    return data
def add_holding(stock_name, quantity, buy_price, current_price, buy_date):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO portfolio_holdings
    (stock_name, quantity, buy_price, current_price, buy_date)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        stock_name,
        quantity,
        buy_price,
        current_price,
        buy_date
    ))

    conn.commit()
    conn.close()


def get_holdings():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM portfolio_holdings
    """)

    data = cursor.fetchall()

    conn.close()

    return data

def add_holding(stock_name, quantity, buy_price, current_price, buy_date):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO portfolio_holdings
        (stock_name, quantity, buy_price, current_price, buy_date)
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        stock_name,
        quantity,
        buy_price,
        current_price,
        buy_date
    ))

    conn.commit()
    conn.close()  
def get_portfolio():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT stock_name, quantity, buy_price, current_price, buy_date
    FROM portfolio_holdings
    """)

    data = cursor.fetchall()

    conn.close()

    return data

    

    
    
        







