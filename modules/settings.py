# JKJ AI Trader Settings

# Application name
APP_NAME = "JKJ AI Trader"

# Version
APP_VERSION = "MVP v0.1"

# Investment defaults
DEFAULT_CAPITAL = 50000

# Risk management
MAX_SINGLE_STOCK_ALLOCATION = 40
MAX_PORTFOLIO_STOCKS = 4

# Trading modes
ENABLE_INTRADAY = True
ENABLE_NORMAL_INVESTMENT = True

# Default risk level
DEFAULT_RISK_LEVEL = "Medium"

# Database location
DATABASE_PATH = "database/jkj_ai.db"


def get_app_settings():
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "default_capital": DEFAULT_CAPITAL,
        "max_single_stock_allocation": MAX_SINGLE_STOCK_ALLOCATION,
        "max_portfolio_stocks": MAX_PORTFOLIO_STOCKS,
        "intraday_enabled": ENABLE_INTRADAY,
        "normal_investment_enabled": ENABLE_NORMAL_INVESTMENT,
        "risk_level": DEFAULT_RISK_LEVEL,
        "database_path": DATABASE_PATH
    }
