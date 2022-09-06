import pandas as pd
import datetime

ORDERS_URL = "./data/hub-orders.csv"

def load_orders():
    data = pd.read_csv(ORDERS_URL, thousands=',')
    lowercase = lambda x: str(x).lower()
    to_month = lambda dt: datetime.date(dt.year, dt.month, 1)
    data.rename(lowercase, axis='columns', inplace=True)
    data["order date"] = pd.to_datetime(data["order date"])
    data["distribution date"] = pd.to_datetime(data["distribution date"])
    data["distribution month"] = data["distribution date"].map(to_month)
    return data

print("generating cleaned order csv")
orders = load_orders()
by_month_site = orders.groupby(by=['location', 'distribution month'])['order total'].sum()
by_month_site.to_csv('./data/by-month-site.csv')
print("All done!")