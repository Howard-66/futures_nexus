from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import commodity
import akshare as ak
from datetime import datetime, timedelta

app = Dash(external_stylesheets=[dbc.themes.FLATLY])

# 创建主品种数据
symbol_id = 'RB'
symbol_name = '螺纹钢'
fBasePath = 'steel/data/mid-stream/螺纹钢/'
json_file = './steel/setting.json'
chain_id = 'steel'
chain_name = '黑色金属'
symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)
symbol_chain = commodity.SymbolChain(chain_id, chain_name, json_file)
page_property = {
    'symbol_id': 'RB',
    'symbol_name': '螺纹钢',
    'json_file': './steel/setting.json',
    'json_file': './steel/setting.json',
    'chain_id': 'steel',
    'chain_name': '黑色金属',
    'symbol': {},
    'symbol_chain': {},
    'symbol_figure': {},
    'chart_setting': {},
}

# 初始化数据
def initial_data():
    # 构造品种数据访问对象
    # symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)
    symbol_j = commodity.SymbolData('J', '焦炭', json_file)
    symbol_i = commodity.SymbolData('I', '铁矿石', json_file)
    symbol_chain.add_symbol(symbol)
    symbol_chain.add_symbol(symbol_j)
    symbol_chain.add_symbol(symbol_i)
    symbol_chain.initialize_data()
    symbol.get_spot_months()
    df_profit = symbol.get_profits(symbol_chain)    

# # 主图全局变量
# main_figure = {}
charts_setting_dict = {}

# 基本面分析配置面板
main_chart_config =dbc.Accordion(
    [
        dbc.AccordionItem(
            [                
                dbc.Label('选择分析指标：', color='darkblue'),
                dbc.Checklist(
                    options=['基差率', '库存', '仓单', '库存消费比', '库存+仓单', '现货利润', '盘面利润', '现货利润+盘面利润'],
                    value=['基差率', '库存', '仓单', '现货利润', '盘面利润'],
                    id='select_index', inline=True
                ),
                html.Hr(),
                dbc.Label('标记区间：', color='darkblue'),
                dbc.Checklist(
                    options=['现货交易月', '指标共振周期'],
                    value=['现货交易月', '指标共振周期'],
                    id='switch_marker',
                    switch=True, inline=True
                ),
                html.Hr(),
                dbc.Label('共振指标设置：', color='darkblue'),
                dbc.Checklist(                    
                    options=['基差率', '库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位', '库存|仓单', '现货利润|盘面利润'],
                    value=['基差率', '库存历史时间分位', '现货利润历史时间分位'],
                    id='select_synchronize_index', inline=True                    
                ),
                html.Hr(),
                dbc.Label('历史分位回溯时间：', color='darkblue'),
                dcc.Slider(
                    0, 130, value=60, step=None,
                    marks={
                        6: '6个月', 12: '1年', 24: '2年', 36: '3年', 60: '5年', 120: '10年', 130: {'label': 'All', 'style': {'color': 'darkblue'}}
                    },
                    id='look_forward_months'
                ),
                html.P(id='config-output'),
            ], 
        title='图表设置'),
    ],
    start_collapsed=True,
    # always_open = True,
    # flush=True,
)

# 基本面分析图表面板（左侧）
tab_main = html.Div([
    # 主框架
    dbc.Row([
        # 左侧面板
        dbc.Col([
            # 配置面板
            dbc.Row(dbc.Form(main_chart_config)),
            # 图表面板
            dbc.Row(
                # dbc.Card(
                #     dbc.CardBody([
                        dcc.Graph(figure={}, id='main-figure-placeholder'),    
                #     ])
                # )
            )                        
        ], width=9),
        # 右侧面板
        dbc.Col([
            # 跨期分析图表
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [
                        html.Div(
                            [
                                html.P(id='figure-click-output'),
                                dbc.Placeholder(size="lg", className="me-1 mt-1 w-100"),
                                dbc.Placeholder(size="lg", className="me-1 mt-1 w-100"),
                                dbc.Placeholder(size="lg", className="me-1 mt-1 w-100"),
                            ])
                        ]
                    ),
                    className="mt-3",
                )
            ),
            # 期限结构分析图表
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [

                        ]
                    ),
                    className="mt-3",
                )
            )
        ], width=3)
    ])
])

tab_setting = dbc.Card(
    dbc.CardBody(
        [
            
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            
        ]
    ),
    className="mt-3",
)

# 品种分析tabview
symbol_tabs = dbc.Tabs(
    [
        dbc.Tab(tab_main, label="基本面分析", tab_id="tab-main"),
        dbc.Tab(tab2_content, label="周期性分析", tab_id="tab-cycle"),
        dbc.Tab(tab2_content, label="跨期套利分析", tab_id="tab-time-cross"),
        dbc.Tab(tab2_content, label="跨品种分析", tab_id="tab-symbol-cross"),
        dbc.Tab(tab2_content, label="交易计划", tab_id="tab-trading-plan"),
        dbc.Tab(tab_setting, label="品种设置", tab_id="tab-config"),
    ],
    id="card-tabs",
    active_tab="tab-main",
)

# 产业链下具体品种分析页面
tab_symbol_rb= dbc.Card(
    dbc.CardBody(
        [
            symbol_tabs
        ]
    ),
    className="mt-3",
)

# 产业链分析tabview
chain_tabs = dbc.Tabs(
    [
        # dbc.Tab(tab_main, label="基本面分析", tab_id="tab-main"),
        dbc.Tab(tab2_content, label="产业链分析", tab_id="tab-overview"),
        dbc.Tab(tab_symbol_rb, label="螺纹钢", tab_id="tab-symbol-rb"),
        dbc.Tab(tab2_content, label="铁矿石", tab_id="tab-symbol-i"),
        dbc.Tab(tab2_content, label="焦炭", tab_id="tab-symbol-l"),
    ],
    id="tabs-chain",
    active_tab="tab-overview",
)        

app.layout = dbc.Container(
    # dbc.Card(
        [
        #     dbc.CardHeader(
                # html.P("FFA Demo", className="card-text")

        #     ),
            # dbc.CardBody(
                chain_tabs,
    #         ),
        ],
    # ),
    className="p-5",
    fluid=True,
)

preivouse_input = {'selected_index': [], 
                   'previous_maker': [], 
                   'previouse_sync_index': [],
                   'previouse_look_forward_months': 0
}

# Add controls to build the interaction
@callback(
    Output(component_id='main-figure-placeholder', component_property='figure'),
    Input('select_index', 'value'),
    Input('switch_marker', 'value'),
    Input('select_synchronize_index', 'value'),
    Input('look_forward_months', 'value')
)
def update_graph(select_index_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value):   
    if symbol_name not in charts_setting_dict:
        charts_setting_dict[symbol_name] = {}
        # initial_data()
        page_property['symbol_figure'] = commodity.SymbolFigure(symbol)
    figure = page_property['symbol_figure'].create_figure(select_index_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value)
    return figure

@app.callback(
    Output('figure-click-output', 'children'),
    Input('main-figure-placeholder', 'clickData'))
def display_click_data(clickData):
    if clickData is not None:
        # 获取第一个被点击的点的信息
        point_data = clickData['points'][0]
        # 获取x轴坐标
        x_value = point_data['x']
        return 'You clicked on x = {}'.format(x_value)
    else:
        return 'No clicks yet'

if __name__ == "__main__":
    initial_data()
    app.run_server(debug=True)
