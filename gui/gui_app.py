# Import packages
from dash import Dash, page_container, page_registry
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from pinon import get_config

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.SLATE]
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

# Main nav bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Peer Groups", href="/peer-groups")),
    ]
)

# App layout
app.layout = dbc.Container([
    dbc.Row(navbar),
    page_container,


], fluid=True)

# Run the app
if __name__ == '__main__':
    # Pinon init
    get_config()
    app.run(debug=True)