import requests
import pandas as pd
import logging
from helper import (
    extract_lines,
    LINE_COLOR_MAP,
    ensure_all_values_present,
    generate_time_blocks,
    get_default_dates,
    format_station_name,
    get_busiest,
)

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")
DATA_DIR = "data/"


def load_data():
    """Load ridership data from file or API."""
    try:
        logger.info("Reading Data file.")
        ridership_df = pd.read_csv(f"{DATA_DIR}data.csv")

    except FileNotFoundError:
        logger.info("Data file not found, fetching from API.")
        ridership_url = "https://data.ny.gov/resource/wujg-7c2s.json?$limit=50000"
        response = requests.get(ridership_url)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            logger.error(f"Failed to fetch data from {ridership_url}")
        return pd.DataFrame()

    return ridership_df


def clean_data(df):
    """Clean and preprocess the ridership data."""
    df["transit_timestamp"] = pd.to_datetime(df["transit_timestamp"])
    df.sort_values("transit_timestamp", ascending=False, inplace=True)
    df["lines"] = df["station_complex"].apply(extract_lines)
    df["station_complex"] = df["station_complex"].apply(format_station_name)
    df["day"] = df["transit_timestamp"].dt.day_name()
    df["hour"] = df["transit_timestamp"].dt.hour
    df["time_block"] = (df["transit_timestamp"].dt.hour // 3) * 3
    df["time_block"] = df["time_block"].apply(lambda x: f"{x:02d}:00-{x+3:02d}:00")
    df["line"] = df["lines"].apply(lambda x: x[0])
    df["line_color"] = df["line"].apply(
        lambda x: (
            LINE_COLOR_MAP[x[0]]
            if len(x) == 1 and x[0] in LINE_COLOR_MAP
            else "#000000"
        )
    )
    df["station_size"] = 7
    df = df[~df["station_complex"].isin(["Central Park North", "RI Tramway"])]
    return df


def filter_data(df, start_date=None, end_date=None):
    """Filter data based on date range."""
    if start_date is None or end_date is None:
        logger.debug("No date range provided, using default dates.")
        start_date, end_date = get_default_dates(df)

    mask = (df["transit_timestamp"] >= start_date) & (
        df["transit_timestamp"] <= end_date
    )
    return df.loc[mask]


def get_hourly_ridership(df: pd.DataFrame) -> pd.DataFrame:
    """Get hourly ridership data."""
    hourly_ridership_df = (
        df.groupby(["transit_timestamp", "borough"])["ridership"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    hourly_ridership_df["total_ridership"] = hourly_ridership_df.iloc[:, 1:].sum(axis=1)
    hourly_ridership_df.columns.name = None  # Remove the MultiIndex column name
    return hourly_ridership_df


def get_stations(ridership_data: pd.DataFrame) -> pd.DataFrame:
    """Get all stations in the dataset."""
    stations_info = ridership_data[
        [
            "station_complex_id",
            "station_complex",
            "latitude",
            "longitude",
            "borough",
            "station_size",
            "line_color",
            "line",
        ]
    ].drop_duplicates(subset=["station_complex"])

    ridership = (
        ridership_data.groupby("station_complex")["ridership"].sum().reset_index()
    )
    stations = pd.merge(stations_info, ridership, on="station_complex", how="left")

    return stations


def get_weekly_ridership(df: pd.DataFrame) -> pd.DataFrame:
    """Get weekly ridership data grouped by day and borough."""

    weekly_ridership_df = (
        df.groupby(["day", "borough"])["ridership"].sum().reset_index()
    )
    weekly_ridership_df.rename(columns={"ridership": "total_ridership"}, inplace=True)
    weekly_ridership_df = ensure_all_values_present(
        weekly_ridership_df,
        ["day", "borough"],
        [df["day"].unique(), df["borough"].unique()],
    )

    station_weekly_ridership_df = (
        df.groupby(["day", "station_complex"])["ridership"].sum().reset_index()
    )
    station_weekly_ridership_df.rename(
        columns={"ridership": "total_ridership"}, inplace=True
    )
    station_weekly_ridership_df = ensure_all_values_present(
        station_weekly_ridership_df,
        ["day", "station_complex"],
        [df["day"].unique(), df["station_complex"].unique()],
    )

    return weekly_ridership_df, station_weekly_ridership_df


def get_time_block_ridership(df: pd.DataFrame) -> pd.DataFrame:
    """Get ridership data grouped by 3-hour time blocks and borough."""

    all_time_blocks = generate_time_blocks()

    time_block_ridership_df = (
        df.groupby(["time_block", "borough"])["ridership"].sum().reset_index()
    )
    time_block_ridership_df.rename(
        columns={"ridership": "total_ridership"}, inplace=True
    )
    time_block_ridership_df = ensure_all_values_present(
        time_block_ridership_df,
        ["time_block", "borough"],
        [all_time_blocks, df["borough"].unique()],
    )

    stations_time_block_ridership_df = (
        df.groupby(["time_block", "station_complex"])["ridership"].sum().reset_index()
    )
    stations_time_block_ridership_df.rename(
        columns={"ridership": "total_ridership"}, inplace=True
    )
    stations_time_block_ridership_df = ensure_all_values_present(
        stations_time_block_ridership_df,
        ["time_block", "station_complex"],
        [all_time_blocks, df["station_complex"].unique()],
    )

    return time_block_ridership_df, stations_time_block_ridership_df


def get_stations_stats_df(df: pd.DataFrame) -> pd.DataFrame:
    """Generate Station Stats with total ridership, avg ridership, peak hour, busiest day."""

    # Total ridership per station
    station_stats_df = (
        df.groupby("station_complex")
        .agg(
            total_ridership=("ridership", "sum"),
            avg_hourly_ridership=("ridership", "mean"),
        )
        .reset_index()
    )
    station_stats_df = station_stats_df.merge(
        df[["station_complex", "lines"]], on="station_complex", how="left"
    ).drop_duplicates(subset=["station_complex"])
    station_stats_df["lines"] = station_stats_df["lines"].apply(lambda x: ", ".join(x))
    station_stats_df.rename(columns={"lines": "line"}, inplace=True)

    # Peak hour per station
    peak_hours = get_busiest(df, ["station_complex", "hour"], "peak_hour")

    # Busiest day of week per station
    busiest_days = get_busiest(df, ["station_complex", "day"], "busiest_day")

    avg_by_day = df.groupby(["station_complex", "day"])["ridership"].sum().reset_index()
    avg_by_day = (
        avg_by_day.groupby("station_complex")["ridership"]
        .mean()
        .reset_index()
        .rename(columns={"ridership": "avg_by_day"})
    )

    # Merge all together
    station_stats_df = station_stats_df.merge(
        peak_hours, on="station_complex", how="left"
    )
    station_stats_df = station_stats_df.merge(
        busiest_days, on="station_complex", how="left"
    )
    station_stats_df = station_stats_df.merge(
        avg_by_day, on="station_complex", how="left"
    )
    station_stats_df = station_stats_df.astype(
        {"total_ridership": int, "avg_hourly_ridership": int, "avg_by_day": int}
    )

    station_stats_df["peak_hour"] = station_stats_df["peak_hour"].apply(
        lambda x: f"{x}:00 AM" if x < 12 else f"{x-12}:00 PM"
    )
    station_stats_df.sort_values(
        by=["station_complex"], inplace=True, ignore_index=True
    )

    station_stats_df = station_stats_df[
        [
            "station_complex",
            "total_ridership",
            "avg_hourly_ridership",
            "peak_hour",
            "busiest_day",
            "avg_by_day",
            "line",
        ]
    ]

    station_stats_df = station_stats_df.rename(
        columns={
            "station_complex": "Station",
            "total_ridership": "Total Ridership",
            "avg_hourly_ridership": "Avg Hourly Ridership",
            "peak_hour": "Peak Hour",
            "busiest_day": "Busiest Day",
            "avg_by_day": "Avg Ridership by Day",
            "line": "Line",
        }
    )

    return station_stats_df


def get_borough_stats_df(df):
    """Generate Borough comparison stats"""

    # Total ridership and station counts per borough
    borough_stats = (
        df.groupby("borough")
        .agg(
            total_ridership=("ridership", "sum"),
            num_stations=("station_complex", "nunique"),
        )
        .reset_index()
    )

    # Average ridership per station
    borough_stats["avg_per_station"] = (
        borough_stats["total_ridership"] / borough_stats["num_stations"]
    ).astype(int)

    # Busiest station per borough
    busiest_stations = get_busiest(
        df, ["borough", "station_complex"], "busiest_station"
    )

    # Average ridership by day
    avg_by_day = df.groupby(["borough", "day"])["ridership"].sum().reset_index()
    avg_by_day = (
        avg_by_day.groupby("borough")["ridership"]
        .mean()
        .reset_index()
        .rename(columns={"ridership": "avg_by_day"})
    )

    station_count = (
        df.groupby("borough")["station_complex"]
        .nunique()
        .reset_index(name="No of Stations")
    )
    line_count = df.groupby("borough")["line"].nunique().reset_index(name="No of Lines")

    # Merge busiest stations
    borough_stats = borough_stats.merge(busiest_stations, on="borough", how="left")
    borough_stats = borough_stats.merge(avg_by_day, on="borough", how="left")
    borough_stats = borough_stats.merge(station_count, on="borough", how="left")
    borough_stats = borough_stats.merge(line_count, on="borough", how="left")

    # Final clean dataframe
    borough_stats = borough_stats[
        [
            "borough",
            "total_ridership",
            "avg_per_station",
            "avg_by_day",
            "busiest_station",
            "No of Stations",
            "No of Lines",
        ]
    ]
    borough_stats["busiest_station"] = borough_stats["busiest_station"].apply(
        format_station_name
    )
    borough_stats = borough_stats.astype(
        {"total_ridership": int, "avg_per_station": int, "avg_by_day": int}
    )
    borough_stats.sort_values(by=["borough"], inplace=True, ignore_index=True)

    borough_stats.rename(
        columns={
            "borough": "Borough",
            "total_ridership": "Total Ridership",
            "avg_per_station": "Avg Ridership per Station",
            "avg_by_day": "Avg Ridership by Day",
            "busiest_station": "Busiest Station",
        },
        inplace=True,
    )

    return borough_stats


def get_line_stats_df(df):
    """Generate line comparison stats"""
    df = df.copy()
    df = df.explode("lines").rename(columns={"lines": "Line"})

    # Total ridership and station counts per line
    line_stats = (
        df.groupby("Line")
        .agg(
            total_ridership=("ridership", "sum"),
            num_stations=("station_complex", "nunique"),
        )
        .reset_index()
    )

    # Average ridership per station
    line_stats["avg_per_station"] = (
        line_stats["total_ridership"] / line_stats["num_stations"]
    ).astype(int)

    # Busiest station per line
    busiest_stations = get_busiest(df, ["Line", "station_complex"], "busiest_station")

    # Average ridership by day
    avg_by_day = df.groupby(["Line", "day"])["ridership"].sum().reset_index()
    avg_by_day = (
        avg_by_day.groupby("Line")["ridership"]
        .mean()
        .reset_index()
        .rename(columns={"ridership": "avg_by_day"})
    )

    station_count = (
        df.groupby("Line")["station_complex"]
        .nunique()
        .reset_index(name="No of Stations")
    )

    # Merge busiest stations
    line_stats = line_stats.merge(busiest_stations, on="Line", how="left")
    line_stats = line_stats.merge(avg_by_day, on="Line", how="left")
    line_stats = line_stats.merge(station_count, on="Line", how="left")

    # Final clean dataframe
    line_stats = line_stats[
        [
            "Line",
            "total_ridership",
            "avg_per_station",
            "avg_by_day",
            "busiest_station",
            "No of Stations",
        ]
    ]
    line_stats["busiest_station"] = line_stats["busiest_station"].apply(
        format_station_name
    )
    line_stats = line_stats.astype(
        {"total_ridership": int, "avg_per_station": int, "avg_by_day": int}
    )
    line_stats.sort_values(by=["Line"], inplace=True, ignore_index=True)
    line_stats.rename(
        columns={
            "total_ridership": "Total Ridership",
            "avg_per_station": "Avg Ridership per Station",
            "avg_by_day": "Avg Ridership by Day",
            "busiest_station": "Busiest Station",
        },
        inplace=True,
    )

    line_stats = line_stats[
        ~line_stats["Line"].isin(["110 St", "Manhattan", "Roosevelt"])
    ]

    return line_stats


def get_key_metrics(df):
    busiest_station = df.groupby("station_complex")["ridership"].sum().idxmax()
    busiest_station = format_station_name(busiest_station)
    max_station_ridership = df.groupby("station_complex")["ridership"].sum().max()

    line_ridership = (
        df.dropna(subset=["lines"]).explode("lines").groupby("lines")["ridership"].sum()
    )
    busiest_line = line_ridership.idxmax()
    max_line_ridership = line_ridership.max()

    busiest_borough = df.groupby("borough")["ridership"].sum().idxmax()
    max_borough_ridership = df.groupby("borough")["ridership"].sum().max()
    no_of_stations = df["station_complex"].nunique()
    total_num_of_rides = df["ridership"].sum()
    no_of_lines = df["line"].nunique()
    no_of_boroughs = df["borough"].nunique()

    metrics = {
        "busiest_station": (busiest_station, int(max_station_ridership)),
        "busiest_line": (busiest_line, int(max_line_ridership)),
        "busiest_borough": (busiest_borough, int(max_borough_ridership)),
        "no_of_stations": no_of_stations,
        "no_of_lines": no_of_lines,
        "no_of_boroughs": no_of_boroughs,
        "total_num_of_rides": int(total_num_of_rides),
    }

    return metrics


def get_data():
    """Load and clean data."""
    ridership_data = load_data()
    ridership_df = clean_data(ridership_data)
    filtered_df = filter_data(ridership_df)
    hourly_ridership_df = get_hourly_ridership(filtered_df)
    weekly_ridership_df, station_weekly_ridership_df = get_weekly_ridership(
        ridership_df
    )
    time_block_ridership_df, stations_time_block_ridership_df = (
        get_time_block_ridership(ridership_df)
    )
    stations_df = get_stations(ridership_df)
    metrics = get_key_metrics(ridership_df)
    station_stats_df = get_stations_stats_df(ridership_df)
    borough_stats_df = get_borough_stats_df(ridership_df)
    line_stats_df = get_line_stats_df(ridership_df)

    return (
        hourly_ridership_df,
        stations_df,
        weekly_ridership_df,
        station_weekly_ridership_df,
        time_block_ridership_df,
        stations_time_block_ridership_df,
        metrics,
        station_stats_df,
        borough_stats_df,
        line_stats_df,
    )
