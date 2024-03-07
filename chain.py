from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

page_property = {
    'dataworks': {},
    'chain_id': 'steel',
    'chain_name': '黑色金属',
    'chain_url': '',
    'variety_url': ''
}

# the style arguments for the sidebar. We use position:fixed and a fixed width
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

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("基本面分析", href="/tab_basis", active="exact"),
                dbc.NavLink("周期性分析", href="/tab_cycle", active="exact"),
                dbc.NavLink("套利分析", href="/tab_arbitrage", active="exact"),
                dbc.NavLink("跨品种分析", href="/tab_cross", active="exact"),
                dbc.NavLink("交易计划", href="/tab_plan", active="exact"),
                dbc.NavLink("品种设置", href="/tab_setting", active="exact"),
                html.Hr(),
                dbc.NavLink("产业链视图", href="/black_metal/chain", active="exact"),
                dbc.NavLink("螺纹钢", href="/black_metal/RB", active="exact"),
                dbc.NavLink("铁矿石", href="/black_metal/I", active="exact"),
                dbc.NavLink("焦炭", href="/J", active="exact"),
            ],
            vertical=True,
            pills=True,
            # fill=True,
            # card=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

tab_overview = html.Div([
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

# 产业链下具体品种分析页面
tab_basis = html.Div([
    dbc.Row([
        # dbc.Col([
        #     sidebar,
        # ]),    
        dbc.Col([
            html.P("basis")
        ])
    ]),
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


page_layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                sidebar,
            ], width=2),
            dbc.Col([
                tab_overview,
            ], 
            width='auto',
            id="main-content"),
        ]),
    ],
)

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

# def callback(app):
    # @app.callback(
        # Output("tab-overview", "children"), 
        # Output("tab-symbol-rb", "children"), 
        # Output("url", "pathname"), 
        # Input("chain-tabs", "active_tab"),
    # )
    # def tab_content(active_tab):
        # global_vars["active_tab"] = active_tab
        # print("on_clic_tab: ", global_vars["active_tab"])
        # if active_tab in global_vars:
        #     return global_vars[active_tab]
        # else:
        #     return "/basis"
        # if active_tab=="tab-overview":
        #     return tab_overview, {}, {}
        # elif active_tab=="tab-symbol-rb":
        #     return {}, tab_basis, {}
        # elif active_tab=="tab-symbol-i":
        #     return {}, {}, tab_basis
        # else:
        #     return {}, {}, {}
        
def page_router(app):
    @app.callback(
        Output("main-content", "children"), 
        # Output("page-content", "children", allow_duplicate=True),
        Input("url", "pathname")
    )
    def nav_page_router(pathname):
        print('Chain Router:', pathname)
        # if '/chain' in pathname:
        #     None
        # elif pathname == "/tab_basis":
        #     None
        return tab_basis
