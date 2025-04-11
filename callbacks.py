from dash import Input, Output, State, no_update
from app_instance import app, data
from helper import add_dash_table
import logging
from data import get_processed_data
from visualizer import get_all_plots

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")
stations_stats_df = data["station_stats_df"]
default_dates = data["dates"]


@app.callback(
    Output("station-details-table", "children"),
    Input("station-map-view", "clickData"),
)
def display_station_details(clickData):
    logger.debug(clickData)
    if clickData is None:
        return None

    station_name = clickData["points"][0]["hovertext"]

    station_data = stations_stats_df[stations_stats_df["Station"] == station_name]
    station_dash_table = add_dash_table(station_data, "station-table")

    return station_dash_table


@app.callback(
    Output("date-picker-start", "date"),
    Output("date-picker-end", "date"),
    Input("url", "pathname"),
)
def on_page_load(pathname):
    """Callback to update date pickers on page load."""
    start_date, end_date = default_dates
    logger.debug(
        f"Page loaded with default start_date: {start_date}, end_date: {end_date}"
    )
    return start_date, end_date


@app.callback(
    # Plots
    Output("ridership-trend-graph", "figure"),
    Output("ridership-weekly-graph", "figure"),
    Output("station-ridership-weekly-graph", "figure"),
    Output("ridership-time-block-graph", "figure"),
    Output("station-ridership-time-block-graph", "figure"),
    Output("station-map-view", "figure"),
    # Tables
    Output("borough-stats-table", "data"),
    Output("line-stats-table", "data"),
    Output("stations-stats-table", "data"),
    # Cards - Row 1
    Output("total-boroughs-card-body", "children"),
    Output("total-lines-card-body", "children"),
    Output("total-stations-card-body", "children"),
    Output("total-rides-card-body", "children"),
    # Cards - Row 2
    Output("busiest-station-card-body", "children"),
    Output("busiest-station-card-para", "children"),
    Output("busiest-line-card-body", "children"),
    Output("busiest-line-card-para", "children"),
    Output("busiest-borough-card-body", "children"),
    Output("busiest-borough-card-para", "children"),
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
        # Load data
        ridership_df = data["ridership_df"]
        new_data = get_processed_data(ridership_df, start_date, end_date)
        new_metrics = new_data["metrics"]
        # Generate plots
        plots = get_all_plots(new_data)

        return (
            # Plots
            plots["hourly_ridership_plot"],
            plots["weekly_ridership_plot"],
            plots["station_weekly_ridership_plot"],
            plots["time_block_ridership_plot"],
            plots["station_time_block_ridership_plot"],
            plots["station_map_view"],
            # Tables
            new_data["borough_stats_df"].to_dict("records"),
            new_data["line_stats_df"].to_dict("records"),
            new_data["station_stats_df"].to_dict("records"),
            # Cards - Row 1
            new_metrics["no_of_boroughs"],
            new_metrics["no_of_lines"],
            new_metrics["no_of_stations"],
            new_metrics["no_of_rides"],
            # Cards - Row 2
            new_metrics["busiest_station"][0],
            f"Total Ridership: {new_metrics['busiest_station'][1]:,}",
            new_metrics["busiest_line"][0],
            f"Total Ridership: {new_metrics['busiest_line'][1]:,}",
            new_metrics["busiest_borough"][0],
            f"Total Ridership: {new_metrics['busiest_borough'][1]:,}",
        )
    return no_update
