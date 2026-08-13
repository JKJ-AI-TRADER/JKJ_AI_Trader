def calculate_holding(stock_name, quantity, buy_price, current_price, buy_date):
    """
    Calculate financial metrics for a single portfolio holding.
    """

    investment = quantity * buy_price
    current_value = quantity * current_price
    profit_loss = current_value - investment

    if investment > 0:
        return_percent = (profit_loss / investment) * 100
    else:
        return_percent = 0

    return {
        "Stock": stock_name,
        "Quantity": quantity,
        "Buy Price": buy_price,
        "Current Price": current_price,
        "Investment": investment,
        "Current Value": current_value,
        "Profit/Loss": profit_loss,
        "Return %": return_percent,
        "Buy Date": buy_date
    }


def calculate_portfolio(holdings):
    """
    Calculate overall portfolio metrics and individual holdings.

    Expected holding format:
    (
        stock_name,
        quantity,
        buy_price,
        current_price,
        buy_date
    )
    """

    results = []

    total_investment = 0
    total_current_value = 0

    for holding in holdings:

        stock_name = holding[0]
        quantity = holding[1]
        buy_price = holding[2]
        current_price = holding[3]
        buy_date = holding[4]

        holding_data = calculate_holding(
            stock_name,
            quantity,
            buy_price,
            current_price,
            buy_date
        )

        results.append(holding_data)

        total_investment += holding_data["Investment"]
        total_current_value += holding_data["Current Value"]

    total_profit_loss = (
        total_current_value - total_investment
    )

    if total_investment > 0:
        portfolio_return = (
            total_profit_loss / total_investment
        ) * 100
    else:
        portfolio_return = 0

    # Calculate portfolio allocation
    for holding in results:

        if total_current_value > 0:
            holding["Allocation %"] = (
                holding["Current Value"]
                / total_current_value
            ) * 100
        else:
            holding["Allocation %"] = 0

    return {
        "holdings": results,
        "total_investment": total_investment,
        "total_current_value": total_current_value,
        "total_profit_loss": total_profit_loss,
        "portfolio_return": portfolio_return,
        "number_of_holdings": len(results)
    }
