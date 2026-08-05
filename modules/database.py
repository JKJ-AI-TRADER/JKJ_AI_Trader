import sqlite3
from pathlib import Path

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

    conn.commit()
    conn.close()


def save_profile(name, capital, risk, intraday, investment):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM investor_profile")

    cursor.execute("""
    INSERT INTO investor_profile
    VALUES (1,?,?,?,?,?)
    """,
    (name, capital, risk, intraday, investment))

    conn.commit()
    conn.close()


def get_profile():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM investor_profile"
    )

    data = cursor.fetchone()

    conn.close()

    return data
