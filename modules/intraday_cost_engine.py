"""
JKJ AI Trader — Intraday Cost Engine V1

Wisdom Before Wealth.

Purpose:
Calculate realistic trading costs and net P&L
before a trade is considered economically viable.

V1 supports:
- NSE Equity Intraday
- NSE Futures
- NSE Options

This version evaluates:
BUY -> SELL trades only.

No broker connection.
No live orders.
No external API.
"""


# -----------------------------------------
# ZERODHA / NSE COST CONSTANTS
# -----------------------------------------

GST_RATE = 0.18

SEBI_RATE = 0.000001
# ₹10 per crore
# 10 / 10,00,00,000 = 0.000001

EQUITY_TRANSACTION_RATE = 0.0000307
# 0.00307%

FUTURES_TRANSACTION_RATE = 0.0000183
# 0.00183%

OPTIONS_TRANSACTION_RATE = 0.0003553
# 0.03553%

EQUITY_STT_SELL_RATE = 0.00025
# 0.025%

FUTURES_STT_SELL_RATE = 0.0005
# 0.05%

OPTIONS_STT_SELL_RATE = 0.0015
# 0.15% on option premium

EQUITY_STAMP_RATE = 0.00003
# 0.003% on buy side

FUTURES_STAMP_RATE = 0.00002
# 0.002% on buy side

OPTIONS_STAMP_RATE = 0.00003
# 0.003% on buy side

MAX_BROKERAGE_PER_ORDER = 20.0


# -----------------------------------------
# MAIN COST ENGINE
# -----------------------------------------

def calculate_intraday_cost(
    instrument_type,
    buy_price,
    sell_price,
    quantity,
    exchange="NSE"
):

    reasons = []
    warnings = []

    # -----------------------------------------
    # INPUT VALIDATION
    # -----------------------------------------

    try:

        buy_price = float(buy_price)
        sell_price = float(sell_price)
        quantity = int(quantity)

    except (
        ValueError,
        TypeError
    ):

        return {
            "Status": "INVALID",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "Invalid trade input."
            ],
            "Warnings": [
                "Buy price, sell price and quantity "
                "must be valid numbers."
            ]
        }

    if buy_price <= 0:

        return {
            "Status": "INVALID",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "Buy price must be greater than zero."
            ],
            "Warnings": []
        }

    if sell_price <= 0:

        return {
            "Status": "INVALID",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "Sell price must be greater than zero."
            ],
            "Warnings": []
        }

    if quantity <= 0:

        return {
            "Status": "INVALID",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "Quantity must be greater than zero."
            ],
            "Warnings": []
        }

    instrument_type = str(
        instrument_type
    ).strip().lower()

    exchange = str(
        exchange
    ).strip().upper()

    if exchange != "NSE":

        return {
            "Status": "UNSUPPORTED",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "V1 currently supports NSE only."
            ],
            "Warnings": []
        }

    supported_types = {
        "equity_intraday",
        "futures",
        "options"
    }

    if instrument_type not in supported_types:

        return {
            "Status": "UNSUPPORTED",
            "Trade Viable": False,
            "Gross P&L": 0.0,
            "Total Costs": 0.0,
            "Net P&L": 0.0,
            "Breakeven Price": 0.0,
            "Reasons": [
                "Unsupported instrument type."
            ],
            "Warnings": [
                "Use equity_intraday, futures or options."
            ]
        }

    # -----------------------------------------
    # TURNOVER
    # -----------------------------------------

    buy_turnover = (
        buy_price * quantity
    )

    sell_turnover = (
        sell_price * quantity
    )

    total_turnover = (
        buy_turnover
        + sell_turnover
    )

    # -----------------------------------------
    # GROSS P&L
    # -----------------------------------------

    gross_pnl = (
        sell_turnover
        - buy_turnover
    )

    # -----------------------------------------
    # BROKERAGE
    # -----------------------------------------

    if instrument_type == "options":

        buy_brokerage = MAX_BROKERAGE_PER_ORDER
        sell_brokerage = MAX_BROKERAGE_PER_ORDER

    else:

        buy_brokerage = min(
            buy_turnover * 0.0003,
            MAX_BROKERAGE_PER_ORDER
        )

        sell_brokerage = min(
            sell_turnover * 0.0003,
            MAX_BROKERAGE_PER_ORDER
        )

    brokerage = (
        buy_brokerage
        + sell_brokerage
    )

    # -----------------------------------------
    # STT
    # -----------------------------------------

    if instrument_type == "options":

        stt = (
            sell_turnover
            * OPTIONS_STT_SELL_RATE
        )

    elif instrument_type == "futures":

        stt = (
            sell_turnover
            * FUTURES_STT_SELL_RATE
        )

    else:

        stt = (
            sell_turnover
            * EQUITY_STT_SELL_RATE
        )

    # -----------------------------------------
    # TRANSACTION CHARGES
    # -----------------------------------------

    if instrument_type == "options":

        transaction_charges = (
            total_turnover
            * OPTIONS_TRANSACTION_RATE
        )

    elif instrument_type == "futures":

        transaction_charges = (
            total_turnover
            * FUTURES_TRANSACTION_RATE
        )

    else:

        transaction_charges = (
            total_turnover
            * EQUITY_TRANSACTION_RATE
        )

    # -----------------------------------------
    # SEBI CHARGES
    # -----------------------------------------

    sebi_charges = (
        total_turnover
        * SEBI_RATE
    )

    # -----------------------------------------
    # STAMP DUTY
    # BUY SIDE ONLY
    # -----------------------------------------

    if instrument_type == "options":

        stamp_duty = (
            buy_turnover
            * OPTIONS_STAMP_RATE
        )

    elif instrument_type == "futures":

        stamp_duty = (
            buy_turnover
            * FUTURES_STAMP_RATE
        )

    else:

        stamp_duty = (
            buy_turnover
            * EQUITY_STAMP_RATE
        )

    # -----------------------------------------
    # GST
    # -----------------------------------------

    gst_base = (
        brokerage
        + transaction_charges
        + sebi_charges
    )

    gst = (
        gst_base
        * GST_RATE
    )

    # -----------------------------------------
    # TOTAL COST
    # -----------------------------------------

    total_costs = (
        brokerage
        + stt
        + transaction_charges
        + sebi_charges
        + stamp_duty
        + gst
    )

    # -----------------------------------------
    # NET P&L
    # -----------------------------------------

    net_pnl = (
        gross_pnl
        - total_costs
    )

    # -----------------------------------------
    # BREAK-EVEN SELL PRICE
    # -----------------------------------------

    # Approximate V1 break-even price.
    #
    # Because some charges depend on sell price,
    # this is calculated iteratively.

    breakeven_price = buy_price

    for _ in range(20):

        estimated_sell_turnover = (
            breakeven_price * quantity
        )

        if instrument_type == "options":

            estimated_sell_brokerage = (
                MAX_BROKERAGE_PER_ORDER
            )

            estimated_stt = (
                estimated_sell_turnover
                * OPTIONS_STT_SELL_RATE
            )

            estimated_transaction = (
                (
                    buy_turnover
                    + estimated_sell_turnover
                )
                * OPTIONS_TRANSACTION_RATE
            )

            estimated_stamp = (
                buy_turnover
                * OPTIONS_STAMP_RATE
            )

        elif instrument_type == "futures":

            estimated_sell_brokerage = min(
                estimated_sell_turnover * 0.0003,
                MAX_BROKERAGE_PER_ORDER
            )

            estimated_stt = (
                estimated_sell_turnover
                * FUTURES_STT_SELL_RATE
            )

            estimated_transaction = (
                (
                    buy_turnover
                    + estimated_sell_turnover
                )
                * FUTURES_TRANSACTION_RATE
            )

            estimated_stamp = (
                buy_turnover
                * FUTURES_STAMP_RATE
            )

        else:

            estimated_sell_brokerage = min(
                estimated_sell_turnover * 0.0003,
                MAX_BROKERAGE_PER_ORDER
            )

            estimated_stt = (
                estimated_sell_turnover
                * EQUITY_STT_SELL_RATE
            )

            estimated_transaction = (
                (
                    buy_turnover
                    + estimated_sell_turnover
                )
                * EQUITY_TRANSACTION_RATE
            )

            estimated_stamp = (
                buy_turnover
                * EQUITY_STAMP_RATE
            )

        estimated_brokerage = (
            buy_brokerage
            + estimated_sell_brokerage
        )

        estimated_sebi = (
            (
                buy_turnover
                + estimated_sell_turnover
            )
            * SEBI_RATE
        )

        estimated_gst = (
            (
                estimated_brokerage
                + estimated_transaction
                + estimated_sebi
            )
            * GST_RATE
        )

        estimated_total_cost = (
            estimated_brokerage
            + estimated_stt
            + estimated_transaction
            + estimated_sebi
            + estimated_stamp
            + estimated_gst
        )

        breakeven_price = (
            buy_price
            + (
                estimated_total_cost
                / quantity
            )
        )

    # -----------------------------------------
    # VIABILITY
    # -----------------------------------------

    if net_pnl > 0:

        status = "PROFITABLE"
        trade_viable = True

        reasons.append(
            "Trade remains profitable after estimated "
            "brokerage and statutory costs."
        )

    elif net_pnl == 0:

        status = "BREAKEVEN"
        trade_viable = False

        reasons.append(
            "Trade only recovers its estimated costs."
        )

        warnings.append(
            "No meaningful net profit remains."
        )

    else:

        status = "LOSS AFTER COSTS"
        trade_viable = False

        reasons.append(
            "Trading costs turn the gross result "
            "into a net loss."
        )

        warnings.append(
            "Gross profit is not sufficient to cover costs."
        )

    # -----------------------------------------
    # COST IMPACT
    # -----------------------------------------

    if gross_pnl != 0:

        cost_impact_percentage = (
            total_costs
            / abs(gross_pnl)
        ) * 100

    else:

        cost_impact_percentage = 0.0

    # -----------------------------------------
    # FINAL RESULT
    # -----------------------------------------

    return {

        "Status": status,

        "Trade Viable": trade_viable,

        "Instrument Type": instrument_type,

        "Exchange": exchange,

        "Buy Price": round(
            buy_price,
            4
        ),

        "Sell Price": round(
            sell_price,
            4
        ),

        "Quantity": quantity,

        "Buy Turnover": round(
            buy_turnover,
            2
        ),

        "Sell Turnover": round(
            sell_turnover,
            2
        ),

        "Total Turnover": round(
            total_turnover,
            2
        ),

        "Gross P&L": round(
            gross_pnl,
            2
        ),

        "Brokerage": round(
            brokerage,
            2
        ),

        "STT": round(
            stt,
            2
        ),

        "Transaction Charges": round(
            transaction_charges,
            2
        ),

        "SEBI Charges": round(
            sebi_charges,
            2
        ),

        "Stamp Duty": round(
            stamp_duty,
            2
        ),

        "GST": round(
            gst,
            2
        ),

        "Total Costs": round(
            total_costs,
            2
        ),

        "Net P&L": round(
            net_pnl,
            2
        ),

        "Cost Impact %": round(
            cost_impact_percentage,
            2
        ),

        "Breakeven Price": round(
            breakeven_price,
            4
        ),

        "Reasons": reasons,

        "Warnings": warnings
    }