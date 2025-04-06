import plotly.express as px
import logging

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")


def plot_hourly_ridership(hourly_ridership_df):
    columns_to_plot = [
        col for col in hourly_ridership_df.columns if col != "transit_timestamp"
    ]
    fig = px.line(
        hourly_ridership_df,
        x="transit_timestamp",
        y=columns_to_plot,
        title="Ridership Over a Day",
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


def plot_weekly_ridership(weekly_ridership_df):
    boroughs = weekly_ridership_df["borough"].unique()
    total_data = (
        weekly_ridership_df.groupby("day")["total_ridership"].sum().reset_index()
    )

    fig = px.bar(
        total_data,
        x="day",
        y="total_ridership",
        title="Ridership Distribution by Day",
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

    buttons = [
        {
            "label": "All Boroughs",
            "method": "update",
            "args": [{"visible": [True] + [False] * len(boroughs)}],
        }
    ]

    for i, borough in enumerate(boroughs):
        borough_data = weekly_ridership_df[weekly_ridership_df["borough"] == borough]
        fig.add_bar(
            x=borough_data["day"],
            y=borough_data["total_ridership"],
            name=borough,
            visible=False,
        )
        buttons.append(
            {
                "label": borough,
                "method": "update",
                "args": [
                    {
                        "visible": [False]
                        + [False] * (i)
                        + [True]
                        + [False] * (len(boroughs) - i - 1)
                    }
                ],
            }
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


def plot_time_block_ridership(time_block_ridership_df):
    boroughs = time_block_ridership_df["borough"].unique()
    total_data = (
        time_block_ridership_df.groupby("time_block")["total_ridership"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        total_data,
        x="time_block",
        y="total_ridership",
        title="Ridership Distribution by Time Block",
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

    buttons = [
        {
            "label": "All Boroughs",
            "method": "update",
            "args": [{"visible": [True] + [False] * len(boroughs)}],
        }
    ]

    for i, borough in enumerate(boroughs):
        borough_data = time_block_ridership_df[
            time_block_ridership_df["borough"] == borough
        ]
        fig.add_bar(
            x=borough_data["time_block"],
            y=borough_data["total_ridership"],
            name=borough,
            visible=False,
        )
        buttons.append(
            {
                "label": borough,
                "method": "update",
                "args": [
                    {
                        "visible": [False]
                        + [False] * i
                        + [True]
                        + [False] * (len(boroughs) - i - 1)
                    }
                ],
            }
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
    )

    # Add click event handling
    station_map.update_traces(
        marker=dict(opacity=0.7), selector=dict(type="scattermapbox")
    )
    station_map.update_layout(clickmode="event+select")

    # Store click state in a variable
    click_state = False

    def handle_click(trace, points, state):
        nonlocal click_state
        click_state = len(points.point_inds) > 0
        print(f"Clicked point: {points.point_inds}")

    station_map.data[0].on_click(handle_click)

    return station_map
