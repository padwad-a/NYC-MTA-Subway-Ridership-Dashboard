import plotly.express as px
import logging
from helper import create_buttons, add_bars_to_figure
import json

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")


def plot_hourly_ridership(hourly_ridership_df):
    columns_to_plot = [
        col for col in hourly_ridership_df.columns if col != "transit_timestamp"
    ]
    fig = px.line(
        hourly_ridership_df,
        x="transit_timestamp",
        y=columns_to_plot,
        labels={
            "transit_timestamp": "Time",
            "value": "No of riders",
            "variable": "Borough",
        },
    )
    fig.for_each_trace(
        lambda t: (
            t.update(name="Total ridership")
            if t.name == "total_ridership"
            else t.update(line=dict(dash="dash"))
        )
    )
    return fig


def plot_weekly_ridership(weekly_ridership_df, key):
    label = "All Boroughs" if key == "borough" else "All Stations"
    unique_keys = weekly_ridership_df[key].unique()
    total_data = (
        weekly_ridership_df.groupby("day")["total_ridership"].sum().reset_index()
    )

    fig = px.bar(
        total_data,
        x="day",
        y="total_ridership",
        labels={
            "day": "Day of the Week",
            "total_ridership": "Number of Riders",
        },
        category_orders={
            "day": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        },
    )

    buttons = create_buttons(unique_keys, label)
    add_bars_to_figure(
        fig, unique_keys, weekly_ridership_df, key, "day", "total_ridership"
    )

    fig.update_layout(
        updatemenus=[
            {
                "buttons": buttons,
                "direction": "down",
                "showactive": True,
                "x": 1.12,
                "y": 1,
            }
        ]
    )

    return fig


def plot_time_block_ridership(time_block_ridership_df, key):
    label = "All Boroughs" if key == "borough" else "All Stations"
    unique_keys = time_block_ridership_df[key].unique()
    total_data = (
        time_block_ridership_df.groupby("time_block")["total_ridership"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        total_data,
        x="time_block",
        y="total_ridership",
        labels={
            "time_block": "Time Block",
            "total_ridership": "Number of Riders",
        },
        category_orders={
            "time_block": [
                f"{hour:02d}:00 - {hour+3:02d}:00" for hour in range(0, 24, 3)
            ]
        },
    )

    buttons = create_buttons(unique_keys, label)
    add_bars_to_figure(
        fig, unique_keys, time_block_ridership_df, key, "time_block", "total_ridership"
    )

    fig.update_layout(
        updatemenus=[
            {
                "buttons": buttons,
                "direction": "down",
                "showactive": True,
                "x": 1.12,
                "y": 1,
            }
        ]
    )

    return fig


def plot_station_map_view(stations_df):
    with open("data/borough_boundaries.geojson", "r") as f:
        borough_boundaries = json.load(f)
    # Ensure required columns exist
    required_cols = {"latitude", "longitude", "station_complex"}
    if not required_cols.issubset(stations_df.columns):
        raise ValueError(
            f"Missing required columns: {required_cols - set(stations_df.columns)}"
        )

    station_map = px.scatter_mapbox(
        stations_df,
        lat="latitude",
        lon="longitude",
        hover_name="station_complex",
        hover_data={
            "borough": True,
            "ridership": True,
            "latitude": False,
            "longitude": False,
            "station_size": False,
            "line_color": False,
        },
        labels={"borough": "Borough", "ridership": "Total ridership"},
        zoom=11,
        height=600,
        size="station_size",
        size_max=7,
        color="line_color",
    )

    station_map.update_layout(
        mapbox_layers=[
            {
                "source": borough_boundaries,
                "type": "line",
                "color": "gray",
                "line": {"width": 1},
            }
        ],
    )

    # Update legend values to use the "line" column
    station_map.for_each_trace(
        lambda t: (
            t.update(
                name=stations_df.loc[stations_df["line_color"] == t.name, "line"].iloc[
                    0
                ]
            )
            if not stations_df.loc[stations_df["line_color"] == t.name, "line"].empty
            else t.update(name=t.name.replace("_", " ").title())
        )
    )

    station_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend_title={"text": "Lines"},
    )

    # Add click event handling
    station_map.update_traces(
        marker=dict(opacity=0.7), selector=dict(type="scattermapbox")
    )
    station_map.update_layout(clickmode="event+select")

    return station_map


def get_all_plots(data):
    plots = {}

    plots["hourly_ridership_plot"] = plot_hourly_ridership(data["hourly_ridership_df"])
    plots["weekly_ridership_plot"] = plot_weekly_ridership(
        data["weekly_ridership_df"], "borough"
    )
    plots["station_weekly_ridership_plot"] = plot_weekly_ridership(
        data["station_weekly_ridership_df"], "station_complex"
    )
    plots["time_block_ridership_plot"] = plot_time_block_ridership(
        data["time_block_ridership_df"], "borough"
    )
    plots["station_time_block_ridership_plot"] = plot_time_block_ridership(
        data["stations_time_block_ridership_df"], "station_complex"
    )
    plots["station_map_view"] = plot_station_map_view(data["stations_df"])

    return plots
