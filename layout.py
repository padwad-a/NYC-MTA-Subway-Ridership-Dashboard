from dash import html, dcc
import dash_bootstrap_components as dbc
from data import load_data, clean_data, filter_data, get_hourly_ridership
from visualizer import plot_hourly_ridership
from buttons import date_picker_start, date_picker_end, load_button

### Data ###
data = load_data()
df = clean_data(data)
filetered_df = filter_data(df)
hourly_ridership_df = get_hourly_ridership(filetered_df)


### Plots ###
hourly_ridership_plot = plot_hourly_ridership(hourly_ridership_df)


def get_layout():
    """Get the layout for the app."""

    ### Tabs ###
    tab1_content = (
        html.Div(
            [
                html.H4("\nRidership Trends Over Time", className="text-center"),
                html.P(
                    "Explore how ridership changes over time", className="text-center"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div([html.Label("Start Date: "), date_picker_start]),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div([html.Label("End Date: "), date_picker_end]),
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
        [html.H4("🗺️ Station-wise Map View"), html.P("Mapping data TBD.")]
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
                    dcc.Tab(label="🕒 Peak Hours Heatmap", value="tab-2"),
                    dcc.Tab(label="🗺️ Station Map View", value="tab-3"),
                    dcc.Tab(label="📊 Borough Comparisons", value="tab-4"),
                ],
            ),
            html.Div(id="tabs-content", className="mt-4"),
        ]
    )
    return layout
