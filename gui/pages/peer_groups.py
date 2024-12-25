import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table

import pinon as pn
from pinon import sql_connection

from gui import get_authorized_user

add_icon = dbc.Button(
    html.I(className="bi bi-plus-circle-fill", style={"font-size": "1.5rem"}),
    color="success",
    className="p-0",
    style={"border-radius": "50%", "width": "48px", "height": "48px"},
    id="add-icon-btn"
)

dash.register_page(__name__)

show_target_input = False
target_input = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.Col(
                    dbc.Input(id="target-input", placeholder="Peer Group Name", type="text"), width= 2
                ),
                dbc.Input(id="peers-input", placeholder="Peer Tickers (comma separated list)", type="text"),
                dbc.Button("Add Peer Group", id="add-peer-group-btn", color="secondary", className="me-2", n_clicks=0)
            ]
        ),
    ],
    style={"display": "block" if show_target_input else "none"}
)

# Dummy data for demonstration purposes
dummy_data = [
    {"Ticker": "AAPL", "Analyze": "Yes"},
    {"Ticker": "GOOG", "Analyze": "No"},
    {"Ticker": "MSFT", "Analyze": "Yes"},
]

analysis_table = html.Div(
    [
        dash_table.DataTable(
            id="analysis-datatable",
            columns=[
                {"name": "Ticker", "id": "Ticker", "type": "text"},
                {"name": "Analyze", "id": "Analyze", "type": "text"},
            ],
            data=dummy_data,
            style_data={
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_header={
                "backgroundColor": "#799DBF",
                "color": "white",
                "fontWeight": "bold",
            },
            style_data_conditional=[],
            row_selectable="single",  # Allows selecting a single row
            active_cell=None,  # Initial state (no cell selected)
        )
    ]
)

# Callback to dynamically update styles based on the selected row
@callback(
    Output("analysis-datatable", "style_data_conditional"),
    Input("analysis-datatable", "active_cell"),
)
def update_styles(active_cell):
    if active_cell:
        # Retrieve the index of the active row
        row_idx = active_cell["row"]
        # Return the style to highlight the active row
        return [
            {
                "if": {"row_index": row_idx},
                "backgroundColor": "#D2F3FF",
                "border": "1px solid #799DBF",
            }
        ]
    # By default, no styles are applied

@callback(
    Output('placeholder-out', 'children'),
    Input('analysis-datatable', 'active_cell'),
)
def display_selected_row(active_cell):
    if active_cell:
        row_index = active_cell['row']
        print(f"Selected row index: {row_index}")
        return f"Selected row index: {row_index}"
    print("No row selected")
    return "No row selected"

# Page layout
layout = dbc.Container([
    html.Br(),
    html.H1('Analysis Targets'),
    html.Br(),
    add_icon,
    analysis_table,
    target_input,
    html.Br(),
    html.Div(id='placeholder-out'),
])


# @callback(
#     Output(component_id='placeholder-out', component_property='children'),
#     Input('add-peer-group-btn', 'n_clicks'),
#     State('target-input', 'value'),
#     State('peers-input', 'value'),
# )
# def add_target(n_clicks, target, peers):
#     err_messages = []
#     if target is None or peers is None:
#         err_messages.append('Enter target ticker and at least one peer')
#         return
#     peers_list = [item.strip().upper() for item in peers.split(',')]
#     peers_list.insert(0, target.upper())
#     companies = pn.Companies()
#
#     peer_companies = [companies.get_company(peer) for peer in peers_list]
#
#     user = get_authorized_user()
#     sql_conn = sql_connection()
#
#
#     app_db = pn.AppDb(sql_conn)
#     app_db.create_peer_group(user_id=user['id'], name=peer_companies[0].name)
#
#     # if target_company is None:
#     #     err_messages.append(f'Target ticker {target} was not found')
#
#
#     print('Break')
#     return f"{target}, {peers}, {n_clicks}"