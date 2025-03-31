from venv import logger
import requests
import pandas as pd
from sympy import N


def load_data():
    # url = "https://data.ny.gov/resource/wujg-7c2s.json?$limit=50000"
    # response = requests.get(url)
    # data = response.json()
    # df = pd.DataFrame(data)
    df = pd.read_csv("data.csv")
    return df


def clean_data(df):
    df["transit_timestamp"] = pd.to_datetime(df["transit_timestamp"])
    df.sort_values("transit_timestamp", ascending=False, inplace=True)

    return df


def get_default_dates(df):
    """Get default start and end dates based on the data."""
    df.sort_values("transit_timestamp", ascending=False, inplace=True)
    end_date = df.loc[0, "transit_timestamp"].date()
    start_date = pd.Timestamp(end_date)
    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = pd.Timestamp(end_date).replace(
        hour=0, minute=0, second=0
    ) + pd.Timedelta(days=1)

    return start_date, end_date


def filter_data(df, start_date=None, end_date=None):
    """Filter data based on date range."""
    if start_date is None or end_date is None:
        logger.debug("No date range provided, using default dates.")
        start_date, end_date = get_default_dates(df)

    mask = (df["transit_timestamp"] >= start_date) & (
        df["transit_timestamp"] <= end_date
    )
    filtered_df = df.loc[mask]
    return filtered_df


def get_hourly_ridership(df):
    hourly_ridership_df = df.copy()
    hourly_ridership_df = (
        hourly_ridership_df.groupby("transit_timestamp")["ridership"]
        .sum()
        .reset_index()
        .rename(columns={"ridership": "hourly_ridership"})
    )
    return hourly_ridership_df
