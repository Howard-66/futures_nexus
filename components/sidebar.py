import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

tab_quick_access = html.Div([
    dcc.Tabs(id="tabs-inline", value='chain', children=[
        dcc.Tab(label='板块', value='chain', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='自选', value='favorite', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='最近', value='recent', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline-3')
])

card_content = [
    dbc.CardHeader("快速入口"),
    dbc.CardBody(
        [
            tab_quick_access,
        ]
    ),
]

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("产业链视图", active=True, href="#")),
        dbc.NavItem(dbc.NavLink("螺纹钢", href="#")),
        dbc.NavItem(dbc.NavLink("铁矿石", href="#")),
        dbc.NavItem(dbc.NavLink("焦炭", disabled=True, href="#")),
    ],
    vertical="md",
)

accordion = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                nav, 
                title="板块品种"
            ),
            dbc.AccordionItem(
                nav, 
                title="自选品种"
            ),
            dbc.AccordionItem(
                nav, 
                title="最近打开"
            ),
        ],
        flush=True,
    ),
)

def get_sidebar(chain_name =''):
    layout = html.Div(
        [
            dbc.Row(html.P('Search')),
            # dbc.Row(dbc.Card(card_content, color="primary", outline=True), className="mb-4",),
            dbc.Row(accordion),
        ],
    )
    return layout

# @callback(Output('tabs-content-inline-3', 'children'),
#               Input('tabs-inline', 'value'))
# def render_content(tab):
#     if tab == 'tab-1':
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
#     elif tab == 'tab-2':
#         return html.Div([
#             html.H3('Tab content 2')
#         ])
#     elif tab == 'tab-3':
#         return html.Div([
#             html.H3('Tab content 3')
#         ])
#     elif tab == 'tab-4':
#         return html.Div([
#             html.H3('Tab content 4')
#         ])