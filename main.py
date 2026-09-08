from src.data_loader import load_sales_data

df = load_sales_data("data/fishmonger_sales.csv")

print(df.head())
print(df.info())
print(df.dtypes)