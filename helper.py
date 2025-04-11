import logging
import re
import pandas as pd
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

logger = logging.getLogger("MTA_Subway_Ridership_Dashboard")

# Define line colors based on MTA standards
LINE_COLOR_MAP = {
    "1": "#EE352E",
    "2": "#EE352E",
    "3": "#EE352E",
    "4": "#00933C",
    "5": "#00933C",
    "6": "#00933C",
    "7": "#B933AD",
    "A": "#2850AD",
    "C": "#2850AD",
    "E": "#2850AD",
    "B": "#FF6319",
    "D": "#FF6319",
    "F": "#FF6319",
    "M": "#FF6319",
    "G": "#6CBE45",
    "J": "#996633",
    "Z": "#996633",
    "L": "#A7A9AC",
    "N": "#FCCC0A",
    "Q": "#FCCC0A",
    "R": "#FCCC0A",
    "W": "#FCCC0A",
    "S": "#808183",
}

# Buttons
date_picker_start = dcc.DatePickerSingle(
    id="date-picker-start",
    className="me-2",
)

date_picker_end = dcc.DatePickerSingle(
    id="date-picker-end",
    className="me-2",
)

load_button = dbc.Button(
    "Load",
    id="load-button",
    color="primary",
    className="ms-2",
)


# Utility functions
def ensure_all_values_present(df, group_columns, unique_values, fill_value=0):
    """Ensure all unique values are present for the given group columns."""
    multi_index = pd.MultiIndex.from_product(unique_values, names=group_columns)
    return (
        df.set_index(group_columns)
        .reindex(multi_index, fill_value=fill_value)
        .reset_index()
    )


def generate_time_blocks():
    """Generate all possible 3-hour time blocks."""
    return [f"{hour:02d}:00-{hour+3:02d}:00" for hour in range(0, 24, 3)]


def get_default_dates(df):
    """Get default start and end dates based on the data."""
    df = df.copy()
    df = df.sort_values("transit_timestamp", ascending=False).reset_index(drop=True)
    end_date = df.iloc[0]["transit_timestamp"]
    start_date = df.iloc[-1]["transit_timestamp"]
    return start_date, end_date


def log_function_call(func):
    """Decorator to log the function name and parameters when called."""

    def wrapper(*args, **kwargs):
        logger.debug(
            f"Function called: {func.__name__} with args: {args} and kwargs: {kwargs}"
        )
        return func(*args, **kwargs)

    return wrapper


def extract_lines(station):
    """Extract lines from station name."""
    lines_txt = re.findall(r"\((.*?)\)", station)
    lines = []

    for line in lines_txt:
        line = line.split(",")
        if len(line) > 0:
            line = [l.strip() for l in line]
            lines += line

    lines = sorted(list(set(lines)))

    return lines


def create_buttons(unique_keys, label):
    """
    Create buttons for interactive dropdown menus in Plotly figures.
    """
    wrap_size = 10
    buttons = [
        {
            "label": label,
            "method": "update",
            "args": [{"visible": [True] + [False] * len(unique_keys)}],
        }
    ]

    for i, value in enumerate(unique_keys):
        buttons.append(
            {
                "label": "<br>".join(
                    value[j : j + wrap_size] for j in range(0, len(value), wrap_size)
                ),
                "method": "update",
                "args": [
                    {
                        "visible": [False]
                        + [False] * i
                        + [True]
                        + [False] * (len(unique_keys) - i - 1)
                    }
                ],
            }
        )
    return buttons


def add_bars_to_figure(fig, unique_keys, data, key, x_col, y_col):
    """
    Add bar traces to a Plotly figure for each unique key.
    """
    for value in unique_keys:
        curr_data = data[data[key] == value]
        fig.add_bar(
            x=curr_data[x_col],
            y=curr_data[y_col],
            name=value,
            visible=False,
        )


def add_dash_table(df: pd.DataFrame, id) -> dash_table.DataTable:
    """
    Create a Dash DataTable from a DataFrame.
    """
    table = dash_table.DataTable(
        id=id,
        sort_action="native",
        columns=[
            {
                "name": col,
                "id": col,
                "deletable": False,
                "selectable": True,
            }
            for col in list(df.columns)
        ],
        data=df.to_dict("records"),
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "maxHeight": "400px",
            "border": "1px solid #ddd",
        },
        style_cell={
            "textAlign": "center",
            "padding": "10px",
            "fontSize": "0.9rem",
            "backgroundColor": "#d9f2fa",
            "border": "1px solid #ddd",
            "fontFamily": "Lato",
        },
        style_header={
            "backgroundColor": "#c0d1e8",
            "fontWeight": "bold",
            "border": "1px solid #ddd",
            "fontFamily": "Lato",
        },
        style_data={
            "border": "1px solid #ddd",
        },
    )

    return table


def add_card(card_header, card_body, card_color, card_style, id, card_para=None):
    """
    Create a Dash card component with a title and content.
    """
    card = dbc.Card(
        [
            dbc.CardHeader(
                card_header, style={"fontFamily": "Lato"}, id=f"{id}-header"
            ),
            dbc.CardBody(
                [
                    html.H5(
                        card_body,
                        className="card-title",
                        style={"fontFamily": "Lato"},
                        id=f"{id}-body",
                    ),
                    html.P(
                        card_para,
                        className="card-text",
                        style={"fontFamily": "Lato"},
                        id=f"{id}-para",
                    ),
                ]
            ),
        ],
        color=card_color,
        inverse=False,
        style=card_style,
        id=id,
    )

    return card


def format_station_name(station_name):
    """Remove parenthesis and extra spaces from station names."""
    return re.sub(r"\s*\(.*?\)", "", station_name)


def get_busiest(df, group_by, result_col):
    """Get the busiest entity (e.g., station, line, borough) based on ridership."""
    value_col = "ridership"
    busiest = (
        df.groupby(group_by)[[value_col]]
        .sum()
        .reset_index()
        .sort_values([group_by[0], value_col], ascending=[True, False])
        .drop_duplicates(subset=[group_by[0]])
        .rename(columns={group_by[1]: result_col})
    )
    return busiest
