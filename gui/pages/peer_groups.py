import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table

import pinon as pn
from pinon import sql_connection

from gui import get_authorized_user

dash.register_page(__name__, "/peer-groups")
# Page layout
layout = dbc.Container([
    html.Br(),
    html.H1('Peer Groups'),
    html.Br(),
    html.Br(),
])

add_pg_button = dbc.Button("Create a Peer Group", id="add-pg-button", className="me-2", n_clicks=0)
layout.children.append(add_pg_button)

@callback(
    Output("url", "href"),
    # Output("url", "refresh"),

    [Input("add-pg-button", "n_clicks")],
    prevent_initial_call=True
)
def on_add_pg_button(n):
    # if n != 0:
    #     return "/create-peer-group", True
    # return "/peer-groups", False

    if n != 0:
        return "/create-peer-group"
    return "/peer-groups"

# Dummy data for demonstration purposes
dummy_data = [
    {"Ticker": "AAPL", "Analyze": "Red"},
    {"Ticker": "GOOG", "Analyze": "Red"},
    {"Ticker": "MSFT", "Analyze": "White"},
]

STYLE_HEADER = {
    "backgroundColor": "#799DBF",
    "color": "white",
    "fontWeight": "bold",
}

STYLE_DATA = {
    "whiteSpace": "normal",
    "height": "auto",
}

COLUMNS = [
    {"name": "Name", "id": "Name", "type": "text"},
    {"name": "Tickers", "id": "Ticker", "type": "text"},
    {"name": "Analyze", "id": "Analyze", "presentation": "dropdown"},
]

DROP_DOWN = {
    'Analyze': {
        'options': [{'label': 'Red', 'value': 'Red'}, {'label': 'White', 'value': 'White'}, {'label': 'Blue', 'value': 'Blue'}]
    }
}
DROP_DOWN_CONDITIONAL = [{
    'if': {
        'column_id': 'Analyze',
        'filter_query': '{row_id} eq 1'
    },
    'options': [{'label': 'RED', 'value': 'Red'}, {'label': 'WHITE', 'value': 'White'},
                {'label': 'BLUE', 'value': 'Blue'}]
}]

peer_groups_table = html.Div(
    [
        dash_table.DataTable(
            id="peer-group-datatable",
            columns=COLUMNS,
            # dropdown_conditional=DROP_DOWN_CONDITIONAL,
            dropdown=DROP_DOWN,
            editable=True,
            data=dummy_data,
            # style_data=STYLE_DATA,
            # style_header=STYLE_HEADER,
            # style_data_conditional=[],
            # row_selectable="single",  # Allows selecting a single row
            active_cell=None,  # Initial state (no cell selected)
        )
    ]
)
layout.children.append(peer_groups_table)

# Temp
temp_alert = dbc.Alert(id='temp-alert')
layout.children.append(temp_alert)

# Callback to dynamically update styles based on the selected row
@callback(
    Output("peer-group-datatable", "style_data_conditional"),
    Input("peer-group-datatable", "active_cell"),
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

# @callback(
#     Output('temp_alert', 'children'),
#     Input('peer-group-datatable', 'active_cell'),
# )
# def display_selected_row(active_cell):
#     if active_cell:
#         row_index = active_cell['row']
#         print(f"Selected row index: {row_index}")
#         return f"Selected row index: {row_index}"
#     print("No row selected")
#     return "No row selected"

# First row editable
@callback(
    Output("peer-group-datatable", "editable"),  # Control the 'editable' property
    Input("peer-group-datatable", "active_cell"),  # Detect the currently active cell
)
def limit_editability(active_cell):
    # Check if the active cell is in the first row (row_index = 0)
    if active_cell is not None and active_cell["row"] == 0:
        return True  # Allow editing

    # Otherwise, make the row non-editable
    return False


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