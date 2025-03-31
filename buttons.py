from dash import html, dcc
import dash_bootstrap_components as dbc

### Tab 1 Buttons ###
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
