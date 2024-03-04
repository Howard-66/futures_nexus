from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

page_property = {
    'dataworks': {},
    'chain_id': 'steel',
    'chain_name': '黑色金属',
}

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE2 = {
    # "position": "fixed",
    "top": 150,
    "left": -10,
    "bottom": 0,
    "width": "9rem",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_STYLE = {
}

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("基本面分析", href="/basis", active="exact"),
                dbc.NavLink("周期性分析", href="/cycle", active="exact"),
                dbc.NavLink("套利分析", href="/arbitrage", active="exact"),
                dbc.NavLink("跨品种分析", href="/chain", active="exact"),
                dbc.NavLink("交易计划", href="/plan", active="exact"),
                dbc.NavLink("品种设置", href="/setting", active="exact"),
                html.Hr(),
                dbc.NavLink("产业链视图", href="/black_metal/chain", active="exact"),
                dbc.NavLink("螺纹钢", href="/black_metal/RB", active="exact"),
                dbc.NavLink("铁矿石", href="/black_metal/I", active="exact"),
                dbc.NavLink("焦炭", href="/J", active="exact"),
            ],
            vertical=True,
            # pills=True,
            fill=True,
            card=True,
        ),
    ],
    style=SIDEBAR_STYLE2,
)

tab_overview = html.Div([
    dbc.Card(    
        dbc.CardBody(
            [
                
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
        dcc.Location(id='url-chain', refresh=False),
        dbc.Row([
            dbc.Col([
                sidebar,
            ], width=2),
            dbc.Col([
                dbc.Row([
                    # chain_tabs,
                ]),
            ],width='12'),
        ]),
    ],
)

def layout(pathname):
    print(chain_tabs.active_tab, global_vars["active_tab"])
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
        
# def page_router(app):
#     @app.callback(
#         Output("tab-symbol-rb", "children", allow_duplicate=True), 
#         Input("url-chain", "pathname")
#     )
#     def nav_page_router(pathname):
#         print('nav_page_router', pathname)
#         if pathname == "/basis":
#             return tab_variety
