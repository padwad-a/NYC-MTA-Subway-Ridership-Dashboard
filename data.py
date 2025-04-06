import stat
import requests
import pandas as pd
import logging
from helper import extract_lines

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")

# Define line colors based on MTA standards
LINE_COLOR_MAP = {
    "1": "#EE352E",
    "2": "#EE352E",
    "3": "#EE352E",
    "4": "#00933C",
    "5": "#00933C",
    "6": "#00933C",
    "7": "#B933AD",
    "A": "#2850AD",
    "C": "#2850AD",
    "E": "#2850AD",
    "B": "#FF6319",
    "D": "#FF6319",
    "F": "#FF6319",
    "M": "#FF6319",
    "G": "#6CBE45",
    "J": "#996633",
    "Z": "#996633",
    "L": "#A7A9AC",
    "N": "#FCCC0A",
    "Q": "#FCCC0A",
    "R": "#FCCC0A",
    "W": "#FCCC0A",
    "S": "#808183",
}


def load_data():
    def get_data_from_api(url):
        response = requests.get(url)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            logger.error(f"Failed to fetch data from {url}")
        return pd.DataFrame()

    # ridership_url = "https://data.ny.gov/resource/wujg-7c2s.json?$limit=50000"
    # ridership_df = get_data_from_api(ridership_url)

    ridership_df = pd.read_csv("data.csv")
    return ridership_df


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


def get_hourly_ridership(df: pd.DataFrame) -> pd.DataFrame:
    """Get hourly ridership data."""
    hourly_ridership_df = df.copy()
    hourly_ridership_df = (
        hourly_ridership_df.groupby(["transit_timestamp", "borough"])["ridership"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    hourly_ridership_df["total_ridership"] = hourly_ridership_df.iloc[:, 1:].sum(axis=1)
    hourly_ridership_df.columns.name = None  # Remove the MultiIndex column name
    return hourly_ridership_df


def get_stations(ridership_data: pd.DataFrame) -> pd.DataFrame:
    """Get all stations in the dataset."""

    # Getting all unique station complexes from the ridership data
    stations_info = ridership_data[
        ["station_complex_id", "station_complex", "latitude", "longitude", "borough"]
    ].drop_duplicates(subset=["station_complex"])

    # Summing and adding ridership data to the stations info
    ridership = (
        ridership_data.groupby("station_complex")["ridership"].sum().reset_index()
    )
    stations = pd.merge(stations_info, ridership, on="station_complex", how="left")
    stations["lines"] = stations["station_complex"].apply(extract_lines)
    stations["line"] = stations["lines"].apply(lambda x: x[0])
    stations.loc[stations["station_complex_id"].str.contains("TRAM"), "line"] = "TRAM"
    stations["line_color"] = stations["line"].apply(
        lambda x: (
            LINE_COLOR_MAP[x[0]]
            if len(x) == 1 and x[0] in LINE_COLOR_MAP
            else "#000000"
        )
    )

    stations["station_size"] = 7
    return stations


def get_data():
    """Load and clean data."""
    ridership_data = load_data()
    ridership_df = clean_data(ridership_data)
    filetered_df = filter_data(ridership_df)
    hourly_ridership_df = get_hourly_ridership(filetered_df)
    stations_df = get_stations(ridership_df)

    return hourly_ridership_df, stations_df
