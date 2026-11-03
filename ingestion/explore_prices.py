import sys
import pandas as pd

path = sys.argv[1]
df = pd.read_csv(path)

print(df.dtypes, "\n")

df = df.rename(columns={
    "MTU (CET/CEST)": "mtu",
    "Area": "area",
    "Day-ahead Price (EUR/MWh)": "price_eur_mwh",
})
df = df[["mtu", "area", "price_eur_mwh"]]

start_text = df["mtu"].str.split(" - ").str[0]
start_cet = pd.to_datetime(start_text, format="%d/%m/%Y %H:%M:%S")
start_cet = start_cet.dt.tz_localize("Europe/Brussels", ambiguous="infer")

df["ts_utc"] = start_cet.dt.tz_convert("UTC")
df["ts_athens"] = start_cet.dt.tz_convert("Europe/Athens")
df["price_eur_mwh"] = pd.to_numeric(df["price_eur_mwh"], errors="coerce")

print("Rows:", len(df))
print("Missing prices:", df["price_eur_mwh"].isna().sum())
print(f"Mean: {df['price_eur_mwh'].mean():.2f} EUR/MWh")
print(f"Min:  {df['price_eur_mwh'].min():.2f} EUR/MWh")
print(f"Max:  {df['price_eur_mwh'].max():.2f} EUR/MWh\n")

hourly = (
    df.set_index("ts_athens")["price_eur_mwh"]
      .resample("1h").mean()
      .round(2)
)
print("Average price per hour (Athens time):")
print(hourly.to_string())
print("\nCheapest hour (Athens):", hourly.idxmin().strftime("%H:%M"), hourly.min())
print("Most expensive hour (Athens):", hourly.idxmax().strftime("%H:%M"), hourly.max())

