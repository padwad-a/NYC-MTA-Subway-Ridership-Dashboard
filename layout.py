from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from helper import (
    add_dash_table,
    add_card,
    date_picker_start,
    date_picker_end,
    load_button,
)
from app_instance import data, plots

hourly_ridership_plot = plots["hourly_ridership_plot"]
weekly_ridership_plot = plots["weekly_ridership_plot"]
station_weekly_ridership_plot = plots["station_weekly_ridership_plot"]
time_block_ridership_plot = plots["time_block_ridership_plot"]
station_time_block_ridership_plot = plots["station_time_block_ridership_plot"]
station_map_view = plots["station_map_view"]
metrics = data["metrics"]
stations_stats_df = data["station_stats_df"]
borough_stats_df = data["borough_stats_df"]
line_stats_df = data["line_stats_df"]


def get_layout():
    """Generate the layout for the app."""
    card_style = {
        "textAlign": "center",
        "padding": "1rem",
        "fontSize": "1.1rem",
        "fontFamily": "Lato",
    }
    heading_style = {"fontFamily": "Gotham"}
    card_color = "light"

    # Ridership Trends Tab
    ridership_trends_tab = html.Div(
        [
            html.H4(
                "📈 Ridership Trends", className="text-center mt-4", style=heading_style
            ),
            html.H5(
                "Ridership Distribution by Day",
                className="text-center mt-4",
                style=heading_style,
            ),
            html.H6("By Boroughs", className="text-center mt-4", style=heading_style),
            dcc.Graph(
                id="ridership-weekly-graph",
                figure=weekly_ridership_plot,
                className="mx-auto",
            ),
            html.H6("By Stations", className="text-center mt-4", style=heading_style),
            dcc.Graph(
                id="station-ridership-weekly-graph",
                figure=station_weekly_ridership_plot,
                className="mx-auto",
            ),
            html.Hr(className="my-4"),
            html.H5(
                "Ridership Distribution by Time Block",
                className="text-center mt-4",
                style=heading_style,
            ),
            html.H6("By Boroughs", className="text-center mt-4", style=heading_style),
            dcc.Graph(
                id="ridership-time-block-graph",
                figure=time_block_ridership_plot,
                className="mx-auto",
            ),
            html.H6("By Stations", className="text-center mt-4", style=heading_style),
            dcc.Graph(
                id="station-ridership-time-block-graph",
                figure=station_time_block_ridership_plot,
                className="mx-auto",
            ),
            html.Hr(className="my-4"),
            html.H5(
                "Ridership Trend over a day",
                className="text-center mt-4",
                style=heading_style,
            ),
            dcc.Graph(
                id="ridership-trend-graph",
                figure=hourly_ridership_plot,
                className="mx-auto",
            ),
        ],
        className="text-center",
        style={"fontFamily": "Lato"},
    )

    # Station Map View Tab
    station_map_view_tab = html.Div(
        [
            html.H4(
                "🗺️ Station Map View", className="text-center mt-4", style=heading_style
            ),
            dcc.Graph(
                id="station-map-view",
                figure=station_map_view,
                config={"scrollZoom": True},
            ),
            html.Hr(className="my-4"),
            html.Div(id="station-details-table"),
        ],
        style={"fontFamily": "Lato"},
    )

    # Statistical Dashboard Tab
    statistical_dashboard_tab = html.Div(
        [
            html.H4(
                "📊 Statistical Dashboard",
                className="text-center mt-4",
                style=heading_style,
            ),
            html.H5(
                "Key Ridership Metrics",
                className="mb-4 text-center",
                style=heading_style,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        add_card(
                            card_header="Total Number of Boroughs",
                            card_body=metrics["no_of_boroughs"],
                            card_color=card_color,
                            card_style=card_style,
                            id="total-boroughs-card",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        add_card(
                            card_header="Total Number of Lines",
                            card_body=metrics["no_of_lines"],
                            card_color=card_color,
                            card_style=card_style,
                            id="total-lines-card",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        add_card(
                            card_header="Total Number of Stations",
                            card_body=metrics["no_of_stations"],
                            card_color=card_color,
                            card_style=card_style,
                            id="total-stations-card",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        add_card(
                            card_header="Total Number of Rides",
                            card_body=metrics["no_of_rides"],
                            card_color=card_color,
                            card_style=card_style,
                            id="total-rides-card",
                        ),
                        width=3,
                    ),
                ],
                justify="center",
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        add_card(
                            card_header="Busiest Station",
                            card_body=metrics["busiest_station"][0],
                            card_color=card_color,
                            card_style=card_style,
                            card_para=f"Total Ridership: {metrics['busiest_station'][1]:,}",
                            id="busiest-station-card",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        add_card(
                            card_header="Busiest Line",
                            card_body=metrics["busiest_line"][0],
                            card_color=card_color,
                            card_style=card_style,
                            card_para=f"Total Ridership: {metrics['busiest_line'][1]:,}",
                            id="busiest-line-card",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        add_card(
                            card_header="Busiest Borough",
                            card_body=metrics["busiest_borough"][0],
                            card_color=card_color,
                            card_style=card_style,
                            card_para=f"Total Ridership: {metrics['busiest_borough'][1]:,}",
                            id="busiest-borough-card",
                        ),
                        md=4,
                    ),
                ],
                justify="center",
            ),
            html.Hr(className="my-4"),
            html.H5(
                "Borough Statistics", className="mb-4 text-center", style=heading_style
            ),
            add_dash_table(df=borough_stats_df, id="borough-stats-table"),
            html.Hr(className="my-4"),
            html.H5(
                "Line Statistics", className="mb-4 text-center", style=heading_style
            ),
            add_dash_table(df=line_stats_df, id="line-stats-table"),
            html.Hr(className="my-4"),
            html.H5(
                "Stations Statistics", className="mb-4 text-center", style=heading_style
            ),
            add_dash_table(df=stations_stats_df, id="stations-stats-table"),
        ],
        style={"fontFamily": "Lato"},
    )

    # Main Layout
    return dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            html.H2(
                "🚇 NYC MTA Subway Ridership Dashboard",
                className="text-center my-4",
                style=heading_style,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    "Start Date: ",
                                    className="me-2",
                                    style={"fontFamily": "Lato"},
                                ),
                                date_picker_start,
                            ]
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    "End Date: ",
                                    className="me-2",
                                    style={"fontFamily": "Lato"},
                                ),
                                date_picker_end,
                            ]
                        ),
                        width="auto",
                    ),
                    dbc.Col(load_button, width="auto"),
                ],
                justify="center",
            ),
            html.Br(),
            dcc.Tabs(
                id="tabs",
                value="tab-1",
                children=[
                    dcc.Tab(
                        label="📊 Statistical Dashboard",
                        value="tab-1",
                        children=[
                            dbc.Spinner(
                                statistical_dashboard_tab,
                                color="primary",
                                type="border",
                                spinner_style={"position": "relative", "zIndex": 10},
                            ),
                        ],
                        style={"fontFamily": "Lato"},
                    ),
                    dcc.Tab(
                        label="📈 Ridership Trends",
                        value="tab-2",
                        children=[
                            dbc.Spinner(
                                ridership_trends_tab,
                                color="primary",
                                type="border",
                                spinner_style={"position": "relative", "zIndex": 10},
                            ),
                        ],
                        style={"fontFamily": "Lato"},
                    ),
                    dcc.Tab(
                        label="🗺️ Station Map View",
                        value="tab-3",
                        children=[
                            dbc.Spinner(
                                station_map_view_tab,
                                color="primary",
                                type="border",
                                spinner_style={"position": "relative", "zIndex": 10},
                            ),
                        ],
                        style={"fontFamily": "Lato"},
                    ),
                ],
            ),
            html.Div(id="tabs-content", className="mt-4"),
        ]
    )
