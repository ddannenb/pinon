# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, page_container, page_registry
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

# Main nav bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Portfolios", href="/portfolios")),
    ]
)
# nav = dbc.Nav(
#     [
#         dbc.NavLink("Home", active=True, href="/"),
#         dbc.NavLink("Portfolios", href="/portfolios"),
#     ]
# )

# App layout
app.layout = dbc.Container([
    dbc.Row(navbar),
    page_container,


], fluid=True)

# Add controls to build the interaction
@callback(
    Output(component_id='my-first-graph-final', component_property='figure'),
    Input(component_id='radio-buttons-final', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)