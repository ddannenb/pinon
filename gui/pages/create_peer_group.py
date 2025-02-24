import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, "/create-peer-group")

# Page layout
layout = dbc.Container([
    html.Br(),
    html.H1('Create Peer Group'),
    html.Br(),
    html.Br(),
])

# Back button
cpg_back_btn = dbc.Button("Back", id="cpg-back-btn", className="me-2", n_clicks=0)
layout.children.append(cpg_back_btn)

@callback(
    Output("url", "href", allow_duplicate=True),
    # Output("url", "refresh", allow_duplicate=True),
    [Input("cpg-back-btn", "n_clicks")],
    prevent_initial_call=True,
)
def on_cpg_back_btn(n):
    # if n != 0:
    #     return "/peer-groups", False
    # return "/create-peer-group", False
    if n != 0:
        return "/peer-groups"
    return "/create-peer-group"

cpg_name = dbc.Input(id="cpg-name", placeholder="Name of Peer Group...", type="text")
layout.children.append(cpg_name)

layout.children.append(html.Div(id='peer-list'))

@callback(Output('peer-list', 'children'),
              [Input('url', 'pathname')])

def on_page_load(path_name):
    return path_name