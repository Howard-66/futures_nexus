from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    # "position": "fixed",
    # "top": 0,
    # "left": 0,
    # "bottom": 0,
    "width": "12rem",
    "height": "100%",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}


tab_overview = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                dbc.Col([
                    html.P("Overview")
                ])
            ]
        ),
    ) 
])

tab_basis = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                dbc.Col([
                    html.P("basis")
                ])
            ]
        ),
    ) 
])

page_layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                # sidebar,
            ], width=2),
            dbc.Col([
                tab_overview,
            ], 
            width='auto',
            id="main-content"),
        ]),
    ],
)

class ChainPage:
    def __init__(self, name) -> None:
        self.chain_name = name
        self.variety_list = self.get_variety_list()
        self.page_maps = {}
        self.active_variety = None
    
    def get_variety_list(self):
        return ['RB', 'I', 'J']
    
    def get_sidebar_layout(self, variety):
        sidebar = html.Div(
            [
                dbc.Nav(
                    [
                        dbc.NavLink("产业链视图", href=f"/chain/{self.chain_name}/overview", active="exact"),
                        dbc.NavLink("螺纹钢", href=f"/chain/{self.chain_name}/RB", active="exact"),
                        dbc.NavLink("铁矿石", href=f"/chain/{self.chain_name}/I", active="exact"),
                        dbc.NavLink("焦炭", href=f"/chain/{self.chain_name}/J", active="exact"),                        
                        html.Hr(),
                        dbc.NavLink("基本面分析", href=f"/chain/{self.chain_name}/{variety}/tab_basis", active="exact"),
                        dbc.NavLink("周期性分析", href=f"/chain/{self.chain_name}/{variety}/tab_cycle", active="exact"),
                        dbc.NavLink("套利分析", href=f"/chain/{self.chain_name}/{variety}/tab_arbitrage", active="exact"),
                        dbc.NavLink("跨品种分析", href=f"/chain/{self.chain_name}/{variety}/tab_cross", active="exact"),
                        dbc.NavLink("交易计划", href=f"/chain/{self.chain_name}/{variety}/tab_plan", active="exact"),
                        dbc.NavLink("品种设置", href=f"/chain/{self.chain_name}/{variety}/tab_setting", active="exact"),
                        html.Div(id='sidebar-content')
                    ],
                    vertical=True,
                    pills=True,
                    # fill=True,
                    # card=True,
                ),
            ],
            style=SIDEBAR_STYLE,
        )
        return sidebar

    def get_page_layout(self, unique_id, sidebar, tab_content):
        left_layout = {}
        if sidebar is None:
            left_layout = {}
        else:
            left_layout = dbc.Col([sidebar,], width=2)
        page_layout = html.Div(
            [
                dbc.Row([
                    left_layout,
                    dbc.Col([
                        tab_content,
                    ], 
                    width='auto',
                    id='main-content'),
                ]),
            ],
        )
        return page_layout
    
    def get_layout(self, variety, analysis_type):
        unique_id = f"{self.chain_name}-{variety}-{analysis_type}"
        tab_content = {}
        if variety == '':
            variety = 'overview' if self.active_variety == None else self.active_variety

        tab_content = html.Div([
            dbc.Card(    
                dbc.CardBody(
                    [
                        dbc.Col([
                            html.P(variety),
                            dbc.Checklist(
                                options=['现货交易月', '指标共振周期'],
                                value=['现货交易月'],
                                id='switch_marker',
                                switch=True, inline=True
                            ),                       
                        ])
                    ]
                ),
            )
        ])

        if variety not in self.page_maps:
            sidebar = self.get_sidebar_layout(variety)
            layout = self.get_page_layout(unique_id, sidebar, tab_content)
            self.page_maps[variety] = layout
        else:
            layout = self.page_maps[variety]

        return layout

    def get_data(self, variety, analysis_type):
        pass

chain_maps = {}

def page_router(chain_name, variety, analysis_type):
    if chain_name not in chain_maps:
        chain_maps[chain_name] = ChainPage(chain_name)
    return chain_maps[chain_name].get_layout(variety, analysis_type)

# def callback(app):
#     @app.callback(
#         Output("tab-overview", "children"), 
#         Output("url", "pathname"), 
#         Input("chain-tabs", "active_tab"),
#     )
#     def do_something(active_tab):
#         pass

page_property = {
    'dataworks': {},
    'chain_id': 'steel',
    'chain_name': '黑色金属',
    'chain_url': '',
    'variety_url': ''
}

tab_overview = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                dbc.Col([
                    html.P("Overview")
                ])
            ]
        ),
    ) 
])

tab_basis = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                dbc.Col([
                    html.P("basis")
                ])
            ]
        ),
    ) 
])

tab_cycle = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                html.P("cycle")
            ]
        ),
    ) 
])

tab_content = dbc.Card(
    dbc.CardBody(
        [
            
        ]
    ),
    className="mt-3",
)

# 产业链分析tabview
chain_tabs = dbc.Tabs(
    [
        dbc.Tab(label="产业链", tab_id="tab-overview", id="tab-overview"),
        dbc.Tab(tab_content, label="基本面分析", tab_id="tab-main"),
        dbc.Tab(tab_content, label="周期性分析", tab_id="tab-cycle"),
        dbc.Tab(tab_content, label="跨期套利分析", tab_id="tab-time-cross"),
        dbc.Tab(tab_content, label="跨品种分析", tab_id="tab-symbol-cross"),
        dbc.Tab(tab_content, label="交易计划", tab_id="tab-trading-plan"),
        dbc.Tab(tab_content, label="品种设置", tab_id="tab-config"),
    ],
    id="chain-tabs",
    active_tab="tab-overview",
)        

global_vars = {
    'active_tab': "tab-overview",
    "tab-overview": "/basis",
}

def layout(pathname):
    page_property["chain_url"] = pathname
    if '/chain' in pathname:
        None
    elif pathname == "/tab_basis":
        None
    # chain_tabs.active_tab = global_vars["active_tab"]
    # for child in chain_tabs.children:
    #     if child.tab_id==global_vars["active_tab"]:
    #         if pathname=='/basis':
    #             print('on_basis')
    #             child.children = tab_basis
    #         elif pathname=='/cycle':
    #             print('on_cycle')
    #             child.children = tab_cycle
    #         else:
    #             child.children = {}
    #     else:
    #         child.children = {}
    #     global_vars[chain_tabs.active_tab] = pathname
    # page_layout.children[1].children[1].children[0].children[0] = chain_tabs
    return page_layout

# 初始化数据
def initialize():
    # dws = dataworks.DataWorks()
    # page_property['dataworks'] = dws
    # symbol = commodity.SymbolData(page_property['symbol_id'], page_property['symbol_name'])
    # page_property['symbol'] = symbol
    # symbol_chain = commodity.SymbolChain(page_property['chain_id'], page_property['chain_name'])
    # page_property['symbol_chain'] = symbol_chain
    # symbol_j = commodity.SymbolData('J', '焦炭')
    # symbol_i = commodity.SymbolData('I', '铁矿石')
    # symbol_chain.add_symbol(symbol)
    # symbol_chain.add_symbol(symbol_j)
    # symbol_chain.add_symbol(symbol_i)
    # symbol_chain.initialize_data(dws)
    return
        
def callback(app):
    @app.callback(
        Output("sidebar-content", "children"), 
        # Output("page-content", "children", allow_duplicate=True),
        Input('switch_marker', "value"),
        State('url', 'pathname')
    )
    def nav_page_router(switch_values, pathname):
        print('Chain Callback:', switch_values, pathname)
        content = html.Div(pathname)
        return content
