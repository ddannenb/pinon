from dash import Dash, page_container
import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.SIMPLEX, dbc.icons.BOOTSTRAP]
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
    app.run(debug=True)