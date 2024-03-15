import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from pages.chain_overview import chain_page_maps
import components.style as style

dash.register_page(__name__, path="/variety/overview")

class VarietyPage:
    def __init__(self, name, chain) -> None:
        self.variety_name = name
        self.chain_name = chain
        # self.page_maps = {}
        self.chain_config = 'futures_nexus/setting/chains.json'
        self.main_content = None

variety_page_maps = {}

def layout(variety_id=None, chain_id=None, **other_unknown_query_strings):
    if variety_id is None:
        return {}
    if chain_id is None or chain_id not in chain_page_maps:
        sidebar = {}
    sidebar = chain_page_maps[chain_id].sidebar
    if variety_id not in variety_page_maps:
        variety_page_maps[variety_id] = VarietyPage(variety_id, chain_id)
        variety_page = variety_page_maps[variety_id]    
        variety_page.main_content = html.Div([
            html.H1(f'This is our {chain_id}-{variety_id} Analytics page'),
            html.Div([
                "Select a city: ",
                dcc.RadioItems(
                    options=['New York City', 'Montreal', 'San Francisco'],
                    value='Montreal',
                    id='analytics-input'
                )
            ]),
            html.Br(),
            html.Div(id='analytics-output'),
        ], style=style.CONTENT_STYLE)
    else:
        variety_page = variety_page_maps[variety_id]    
    layout = html.Div([
        dbc.Row(
            [
                dbc.Col(sidebar,),
                dbc.Col(variety_page.main_content,)
            ],
        )
    ])

    return layout

@callback(
    Output('analytics-output', 'children'),
    Input('analytics-input', 'value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'