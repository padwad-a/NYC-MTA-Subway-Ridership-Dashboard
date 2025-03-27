from dash import html, dcc
import plotly.express as px


def plot_hourly_ridership(hourly_ridership_df):
    fig = px.line(
        hourly_ridership_df,
        x="transit_timestamp",
        y="hourly_ridership",
        title="Ridership Over Time",
    )
    return fig
