"""
JKJ AI Trader

Main application entry point.

Wisdom Before Wealth.
"""

from modules.analysis_engine import analyze_stock
from modules.report_engine import generate_report


def main():

    print("==========================================")
    print("JKJ AI TRADER")
    print("Wisdom Before Wealth.")
    print("==========================================")

    print()
    print("1. Analyse New Investment")
    print("2. Analyse Existing Holding")
    print()

    choice = input("Select option (1 or 2): ").strip()

    if choice not in ["1", "2"]:
        print("Invalid selection.")
        return

    holding_status = choice == "2"

    print()

    symbol = input("Enter stock symbol: ").strip().upper()

    if not symbol:
        print("No stock symbol entered.")
        return

    purchase_price = 0

    # -----------------------------------------
    # EXISTING HOLDING DETAILS
    # -----------------------------------------

    if holding_status:

        print()

        try:
            purchase_price = float(
                input("Enter your purchase price per share: ")
            )

        except ValueError:
            print("Invalid purchase price.")
            return

    print()
    print(f"Analysing {symbol}...")

    try:

        result = analyze_stock(
        symbol,
        holding_status=holding_status,
        purchase_price=purchase_price
    )

        report = generate_report(result)

        print()
        print(report)

    except Exception as error:

        print()
        print("Analysis failed.")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()