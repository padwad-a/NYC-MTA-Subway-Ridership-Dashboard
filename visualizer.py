import plotly.express as px


def plot_hourly_ridership(hourly_ridership_df):
    columns_to_plot = [
        col for col in hourly_ridership_df.columns if col != "transit_timestamp"
    ]
    fig = px.line(
        hourly_ridership_df,
        x="transit_timestamp",
        y=columns_to_plot,
        title="Ridership Over Time",
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
                name=stations_df.loc[stations_df["line_color"] == t.name, "line"].iloc[0]
            )
            if not stations_df.loc[stations_df["line_color"] == t.name, "line"].empty
            else t.update(name=t.name.replace("_", " ").title())
        )
    )

    station_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )

    return station_map
