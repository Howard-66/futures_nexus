import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("产业链视图", active=True, href="#")),
        dbc.NavItem(dbc.NavLink("螺纹钢", href="#")),
        dbc.NavItem(dbc.NavLink("铁矿石", href="#")),
        dbc.NavItem(dbc.NavLink("焦炭", disabled=True, href="#")),
    ],
    vertical="md",
)

card_content = [
    dbc.CardHeader("快速入口"),
    dbc.CardBody(
        [
            nav,
        ]
    ),
]

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "3.5rem",
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "1rem 1rem",
    "backgroundColor": "#f8f9fa",
}

layout = html.Div(
    [
        dbc.Row(html.P('Search')),
        dbc.Row(dbc.Card(card_content, color="primary", outline=True), className="mb-4",),
        # dbc.Row(card_content),
    ],
    style=SIDEBAR_STYLE
)

def get_sidebar(chain_name =''):
    layout = html.Div(
        [
            dbc.Row(html.P('Search')),
            # dbc.Row(dbc.Card(card_content, color="primary", outline=True), className="mb-4",),
            dbc.Row(card_content),
        ],
    )
    return layout

# @callback(Output('tabs-content-inline-3', 'children'), 
#           Input('tabs-inline', 'value'))
# def render_content(tab):
#     if tab == '版块':
#         print(f"On tab: {tab}")
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
    # elif tab == 'tab-2':
    #     return html.Div([
    #         html.H3('Tab content 2')
    #     ])
    # elif tab == 'tab-3':
    #     return html.Div([
    #         html.H3('Tab content 3')
    #     ])
    # elif tab == 'tab-4':
    #     return html.Div([
    #         html.H3('Tab content 4')
    #     ])