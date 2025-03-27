from dash import html, dcc
import dash_bootstrap_components as dbc
from data import load_data, clean_data, get_hourly_ridership
from visualizer import plot_hourly_ridership

### Data ###
data = load_data()
df = clean_data(data)
hourly_ridership_df = get_hourly_ridership(df)


### Plots ###
hourly_ridership_plot = plot_hourly_ridership(hourly_ridership_df)


### Tabs ###
tab1_content = (
    html.Div(
        [
            html.H4("📈 Ridership Trends Over Time"),
            html.P("Explore how ridership changes over time."),
            dcc.Graph(id="ridership-trend-graph", figure=hourly_ridership_plot),
        ]
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
        html.H2("🚇 NYC MTA Subway Ridership Dashboard", className="text-center my-4"),
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(
                    label="📈 Ridership Trends", value="tab-1", children=tab1_content
                ),
                dcc.Tab(label="🕒 Peak Hours Heatmap", value="tab-2"),
                dcc.Tab(label="🗺️ Station Map View", value="tab-3"),
                dcc.Tab(label="📊 Borough Comparisons", value="tab-4"),
            ],
        ),
        html.Div(id="tabs-content", className="mt-4"),
    ]
)
