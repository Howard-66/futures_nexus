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

chain_menu = dbc.Nav(
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
        self.chain_menu = None
        self.chain_overview = None
    
    def get_variety_list(self):
        return self.variety_list

    # 创建侧边导航栏
    def create_sidebar_nav(self, variety):
        side_bar_nav = dbc.Nav(
            [        
            ],
            vertical=True,
            pills=True,
        )
        if variety == 'overview':
            side_bar_nav.children = []
        else:
            side_bar_nav.children = [
                dbc.NavLink("基本面分析", href=f"/chain/{self.chain_name}/{variety}/basis", active="exact"),
                dbc.NavLink("周期性分析", href=f"/chain/{self.chain_name}/{variety}/cycle", active="exact"),
                dbc.NavLink("跨期分析", href=f"/chain/{self.chain_name}/{variety}/cross_period", active="exact"),
                dbc.NavLink("跨品种分析", href=f"/chain/{self.chain_name}/{variety}/cross_variety", active="exact"),
                dbc.NavLink("交易计划", href=f"/chain/{self.chain_name}/{variety}/plan", active="exact"),
            ]
        return side_bar_nav
    
    # 创建产业链品种切换菜单
    def create_chain_menu(self):
        if self.chain_menu is None:
            chain_menu.children = [
                dbc.NavLink("产业链视图", href=f"/chain/{self.chain_name}/overview", active="exact"),
            ]
            for variety in self.variety_list:
                nav_link = dbc.NavLink(variety, href=f"/chain/{self.chain_name}/{variety}", active="exact")
                chain_menu.children.append(nav_link)
            self.chain_menu = chain_menu
        return self.chain_menu
    
    def create_chain_overview(self):
        return html.P("产业链视图")

    # 创建分析页面
    def create_analyzing_layout(self, variety, analysis_type):
        # 根据analysis_type创建分析视图
        if analysis_type == "basis":
            analyzing_layout = html.P(f"{variety}-{analysis_type} page")
        elif analysis_type == "cycle":
            analyzing_layout = html.P(f"{variety}-{analysis_type} page")

        return analyzing_layout
    
    def get_layout(self, variety, analysis_type):        
        chain_menu = self.create_chain_menu()        
        if variety not in self.page_maps: 
            if variety == "overview":
                side_bar_nav = self.create_sidebar_nav(variety)
                analysis_type = None
                analyzing_layout = self.create_chain_overview()
                self.page_maps[variety] = {'sidebar_nav': side_bar_nav, 'active': analysis_type, analysis_type: analyzing_layout}
            else:
                side_bar_nav = self.create_sidebar_nav(variety)
                analysis_type = 'basis'
                analyzing_layout = self.create_analyzing_layout(variety, analysis_type)
                self.page_maps[variety] = {'sidebar_nav': side_bar_nav, 'active': analysis_type, analysis_type: analyzing_layout}
        else:
            side_bar_nav = self.page_maps[variety]['sidebar_nav']
            if analysis_type is None:
                analysis_type = self.page_maps[variety]['active']
            if analysis_type not in self.page_maps[variety]:
                analyzing_layout = self.create_analyzing_layout(variety, analysis_type)
                self.page_maps[variety][analysis_type] = analyzing_layout
                self.page_maps[variety]['active'] = analysis_type
            else:
                analyzing_layout = self.page_maps[variety][analysis_type]
                self.page_maps[variety]['active'] = analysis_type
        main_content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(chain_menu),
                        dbc.Col(index_selector),
                    ],
                ),
                dbc.Row(analyzing_layout),
            ]
        )        
        return side_bar_nav, main_content

    def get_data(self, variety, analysis_type):
        pass

def page_router(chain_name, variety, analysis_type):
    if chain_name not in chain_page_maps:
        chain_page_maps[chain_name] = ChainPage(chain_name)
    return chain_page_maps[chain_name].get_layout(variety, analysis_type)

# def callback(app):
#     @app.callback(
#         Output("sidebar-content", "children"), 
#         # Output("page-content", "children", allow_duplicate=True),
#         Input('switch_marker', "value"),
#         State('url', 'pathname')
#     )
#     def nav_page_router(switch_values, pathname):
#         print('Chain Callback:', switch_values, pathname)
#         content = html.Div(pathname)
#         return content