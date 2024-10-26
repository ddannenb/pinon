import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

import pinon as pn

dash.register_page(__name__)

target_input = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.Col(
                    dbc.InputGroupText("Enter a ticker and its peers"), width=2
                ),
                dbc.Col(
                    dbc.Input(id="ticker-input", placeholder="Target Ticker", type="text"), width= 2
                ),
                dbc.Input(id="peers-input", placeholder="Peer Tickers (comma separated list)", type="text"),
                dbc.Button("Add", id="add-target-btn", color="secondary", className="me-2", n_clicks=0)
            ]
        ),
    ]
)


layout = html.Div([
    html.Br(),
    html.H1('Analysis Targets'),
    html.Br(),
    target_input,
    html.Div(id='placeholder-out'),
])


@callback(
    Output(component_id='placeholder-out', component_property='children'),
    Input('add-target-btn', 'n_clicks'),
    State('ticker-input', 'value'),
    State('peers-input', 'value'),
)
def add_target(n_clicks, ticker, peers):
    companies = pn.Companies()
    temp = companies.get_company(ticker)

    print('Break')
    return f"{ticker}, {peers}, {n_clicks}"