from dash import Input, Output, State, no_update
from app_instance import app
from data import (
    load_data,
    clean_data,
    filter_data,
    get_hourly_ridership,
    get_default_dates,
    get_stations_stats_df,
)
from visualizer import plot_hourly_ridership
from helper import add_dash_table
import logging

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")

data = load_data()
data = clean_data(data)


@app.callback(
    Output("station-details-table", "children"),
    Input("station-map-view", "clickData"),
)
def display_station_details(clickData):
    logger.debug(clickData)
    if clickData is None:
        return None

    station_name = clickData["points"][0]["hovertext"]

    ridership_df = clean_data(load_data())
    station_stats_df = get_stations_stats_df(ridership_df)
    station_data = station_stats_df[station_stats_df["Station"] == station_name]
    station_dash_table = add_dash_table(station_data, "station-table")

    return station_dash_table


@app.callback(
    Output("date-picker-start", "date"),
    Output("date-picker-end", "date"),
    Input("url", "pathname"),
)
def on_page_load(pathname):
    """Callback to update date pickers on page load."""
    start_date, end_date = get_default_dates(data)
    logger.debug(
        f"Page loaded with default start_date: {start_date}, end_date: {end_date}"
    )
    return start_date, end_date


@app.callback(
    Output("ridership-trend-graph", "figure"),
    Input("load-button", "n_clicks"),
    State("date-picker-start", "date"),
    State("date-picker-end", "date"),
)
def update_graph(n_clicks, start_date, end_date):
    """Update the graph based on the selected date range."""
    if n_clicks:
        logger.debug(
            f"Update graph called with start_date: {start_date}, end_date: {end_date}"
        )
        filtered_data = filter_data(data, start_date, end_date)
        hourly_ridership_df = get_hourly_ridership(filtered_data)
        fig = plot_hourly_ridership(hourly_ridership_df)
        return fig
    return no_update
