import time
from dash import html, dcc
import dash_bootstrap_components as dbc
from data import get_data
from visualizer import (
    plot_hourly_ridership,
    plot_station_map_view,
    plot_weekly_ridership,
    plot_time_block_ridership,
)
from buttons import date_picker_start, date_picker_end, load_button

### Data ###
hourly_ridership_df, stations_df, weekly_ridership_df, time_block_ridership_df = (
    get_data()
)


### Plots ###
hourly_ridership_plot = plot_hourly_ridership(hourly_ridership_df)
weekly_ridership_plot = plot_weekly_ridership(weekly_ridership_df)
time_block_ridership_plot = plot_time_block_ridership(time_block_ridership_df)
station_map_view = plot_station_map_view(stations_df)


def get_layout():
    """Get the layout for the app."""

    ### Tabs ###
    tab1_content = (
        html.Div(
            [
                html.H4("Ridership Trends", className="text-center mt-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label("Start Date: ", className="me-2"),
                                    date_picker_start,
                                ]
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label("End Date: ", className="me-2"),
                                    date_picker_end,
                                ]
                            ),
                            width="auto",
                        ),
                        dbc.Col(load_button, width="auto"),
                    ],
                    justify="center",
                ),
                dcc.Graph(
                    id="ridership-trend-graph",
                    figure=hourly_ridership_plot,
                    className="mx-auto",
                ),
                dcc.Graph(
                    id="ridership-weekly-graph",
                    figure=weekly_ridership_plot,
                    className="mx-auto",
                ),
                dcc.Graph(
                    id="ridership-time-block-graph",
                    figure=time_block_ridership_plot,
                    className="mx-auto",
                ),
            ],
            className="text-center",
        ),
    )

    tab2_content = html.Div(
        [
            html.H4("🕒 Heatmap of Hourly Ridership"),
            html.P("This will show heatmaps soon!"),
        ]
    )

    tab3_content = html.Div(
        [
            html.H4("🗺️ Station Map View", className="text-center mt-4"),
            dcc.Graph(
                id="station-map-view",
                figure=station_map_view,
                config={"scrollZoom": True},
            ),
        ]
    )

    tab4_content = html.Div(
        [
            html.H4("📊 Borough-Level Ridership Comparison"),
            html.P("Comparison charts to be added."),
        ]
    )

    ### Layout ###
    layout = dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            html.H2(
                "🚇 NYC MTA Subway Ridership Dashboard", className="text-center my-4"
            ),
            dcc.Tabs(
                id="tabs",
                value="tab-1",
                children=[
                    dcc.Tab(
                        label="📈 Ridership Trends",
                        value="tab-1",
                        children=tab1_content,
                    ),
                    dcc.Tab(
                        label="🕒 Performance Dashboard",
                        value="tab-2",
                        children=tab2_content,
                    ),
                    dcc.Tab(
                        label="🗺️ Station Map View", value="tab-3", children=tab3_content
                    ),
                    dcc.Tab(
                        label="📊 Borough Comparisons",
                        value="tab-4",
                        children=tab4_content,
                    ),
                ],
            ),
            html.Div(id="tabs-content", className="mt-4"),
        ]
    )
    return layout
