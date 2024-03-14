import dash
import json
from dash import html
import dash_bootstrap_components as dbc
import components.style as style
from components.sidebar import get_sidebar
from global_service import gs

dash.register_page(__name__, path="/chain/overview")

# storage chain pages already openned
chain_page_maps = {}

class ChainPage:
    def __init__(self, name) -> None:
        self.chain_name = name
        self.page_maps = {}
        self.chain_config = 'setting/chains.json'
        with open(self.chain_config, encoding='utf-8') as chains_file:
            chains_setting = json.load(chains_file)[self.chain_name]      
        self.variety_list = chains_setting["variety_list"]
        self.side_bar = None
        self.main_content = None
    
    def get_variety_list(self):
        return self.variety_list

def layout(chain_id=None, **other_unknown_query_strings):
    if chain_id is None:
        return {}
    if chain_id not in chain_page_maps:
        chain_page_maps[chain_id] = ChainPage(chain_id)
    chain_page = chain_page_maps[chain_id]
    chain_page.sidebar = get_sidebar(chain_id, gs.variety_id_name_map, chain_page.get_variety_list())
    chain_page.main_content = html.Div(f'This is our Chain-{chain_id} page content.', style=style.CONTENT_STYLE),
    layout = html.Div([
        dbc.Row(
            [
                dbc.Col(chain_page.sidebar,),
                dbc.Col(chain_page.main_content,)
            ],
        )
    ])
    return layout