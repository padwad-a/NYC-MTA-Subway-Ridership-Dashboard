from dash import Input, Output, html
from app import app
from data import load_data, clean_data
import visualizer

data = load_data()
data = clean_data(data)
