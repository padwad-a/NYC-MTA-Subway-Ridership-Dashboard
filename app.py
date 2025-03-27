import dash
import dash_bootstrap_components as dbc
from layout import layout
import callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MTA Subway Ridership Dashboard"
app.layout = layout

if __name__ == "__main__":

    app.run(debug=True)
