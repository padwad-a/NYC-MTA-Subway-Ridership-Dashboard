import dash
import dash_bootstrap_components as dbc
import logging
from data import get_processed_data
from visualizer import get_all_plots

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MTA Subway Ridership Dashboard"

# Set up the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Log to the console
)

# Load data
data = get_processed_data()

# Generate plots
plots = get_all_plots(data)
