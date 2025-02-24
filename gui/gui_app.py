import pathlib

from dash import Dash, page_container, dcc, html
import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme
ASSETS_PATH = pathlib.Path(__file__).parent / "assets"

external_stylesheets = [dbc.themes.SIMPLEX, dbc.icons.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True, assets_folder=str(ASSETS_PATH))


# Main nav bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Peer Groups", href="/peer-groups")),
        dbc.NavItem(dbc.NavLink("Create Peer Group", href="/create-peer-group")),
    ]
)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh='callback-nav'),
    dbc.Row(navbar),
    page_container,
], fluid=True)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)