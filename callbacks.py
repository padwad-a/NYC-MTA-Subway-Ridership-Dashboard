from dash import Input, Output, State, no_update
from app_instance import app
from data import (
    load_data,
    clean_data,
    filter_data,
    get_hourly_ridership,
    get_default_dates,
)
from visualizer import plot_hourly_ridership
import logging

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")

data = load_data()
data = clean_data(data)


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
