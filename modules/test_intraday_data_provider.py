from intraday_data_provider import get_intraday_data


print("========================================")
print("JKJ AI INTRADAY DATA PROVIDER TEST")
print("========================================")

symbol = "RELIANCE"

result = get_intraday_data(symbol)

print("\nSymbol:", result.get("Symbol"))
print("Status:", result.get("Status"))
print("Data Status:", result.get("Data Status"))
print("Interval:", result.get("Interval"))
print("Bars:", result.get("Bars"))

print("\nCurrent Price:", result.get("Current Price"))
print("Open:", result.get("Open"))
print("High:", result.get("High"))
print("Low:", result.get("Low"))
print("Close:", result.get("Close"))
print("Volume:", result.get("Volume"))

print("\n========================================")