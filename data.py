import requests
import pandas as pd


def load_data():
    # url = "https://data.ny.gov/resource/wujg-7c2s.json?$limit=50000"
    # response = requests.get(url)
    # data = response.json()
    # df = pd.DataFrame(data)
    df = pd.read_csv("data.csv")
    return df


def clean_data(df):
    df["transit_timestamp"] = pd.to_datetime(df["transit_timestamp"])
    df.sort_values("transit_timestamp", inplace=True)

    return df


def get_hourly_ridership(df):
    hourly_ridership_df = df.copy()
    hourly_ridership_df = (
        hourly_ridership_df.groupby("transit_timestamp")["ridership"]
        .sum()
        .reset_index()
        .rename(columns={"ridership": "hourly_ridership"})
    )
    return hourly_ridership_df
