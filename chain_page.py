from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json

# 市场全景导航栏
sidebar_nav = dbc.Nav(
    [        
    ],
    vertical=True,
    pills=True,
)

variety_menu = dbc.Nav(
    children=[
    ],
    pills=True,
)

index_selector = dbc.Select(
    options=[
        {'label': '基差-库存-利润', 'value': 'bsp'},
        {'label': '基差-仓单-利润', 'value': 'brp'},
    ],
    size='sm'
)

chain_page_maps = {}

class ChainPage:
    def __init__(self, name) -> None:
        self.chain_name = name
        self.page_maps = {}
        self.active_variety = None
        self.chain_config = 'chains.json'
        with open(self.chain_config, encoding='utf-8') as chains_file:
            chains_setting = json.load(chains_file)[self.chain_name]      
        self.variety_list = chains_setting["variety_list"]
    
    def get_variety_list(self):
        return self.variety_list

    def create_sidebar_nav(self, variety):
        return sidebar_nav

    def get_main_content(self, variety, analysis_type):
        # variety_menu.children = []
        variety_menu.children = [
            dbc.NavLink("产业链视图", href=f"/chain/{self.chain_name}/overview", active="exact"),
        ]
        for variety in self.variety_list:
            variety_nav_link = dbc.NavLink(variety, href=f"/chain/{self.chain_name}/{variety}", active="exact")
            variety_menu.children.append(variety_nav_link)
        main_content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(variety_menu),
                        dbc.Col(index_selector),
                    ],
                ),
                dbc.Row(),
            ]
        )
        return main_content
    
    def get_layout(self, variety, analysis_type):
        if variety not in self.page_maps:
            side_bar_nav = self.create_sidebar_nav(variety)
            main_content = self.get_main_content(variety, analysis_type)
            self.page_maps[variety] = [side_bar_nav, main_content]
        else:
            side_bar_nav, main_content = self.page_maps[variety]

        return side_bar_nav, main_content

    def get_data(self, variety, analysis_type):
        pass

def page_router(chain_name, variety, analysis_type):
    if chain_name not in chain_page_maps:
        chain_page_maps[chain_name] = ChainPage(chain_name)
    return chain_page_maps[chain_name].get_layout(variety, analysis_type)