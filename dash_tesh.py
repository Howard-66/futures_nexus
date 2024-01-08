from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dataworks
import commodity
import akshare as ak
from datetime import datetime, timedelta
from functools import reduce

app = Dash(external_stylesheets=[dbc.themes.FLATLY],           
           prevent_initial_callbacks='initial_duplicate')

# 创建主品种数据
# symbol_id = 'RB'
# symbol_name = '螺纹钢'
# fBasePath = 'steel/data/mid-stream/螺纹钢/'
# json_file = './steel/setting.json'
# chain_id = 'steel'
# chain_name = '黑色金属'
# symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)
# symbol_chain = commodity.SymbolChain(chain_id, chain_name, json_file)
page_property = {
    'dataworks': {},
    'symbol_id': 'RB',
    'symbol_name': '螺纹钢',
    'json_file': './steel/setting.json',
    'chain_id': 'steel',
    'chain_name': '黑色金属',
    'symbol': {},
    'symbol_chain': {},
    'symbol_figure': {},
    'chart_setting': {},
    'term_data': {},
}

# 初始化数据
def initial_data():
    dws = dataworks.DataWorks()
    page_property['dataworks'] = dws
    json_file = page_property['json_file']
    symbol = commodity.SymbolData(page_property['symbol_id'], page_property['symbol_name'], json_file)
    page_property['symbol'] = symbol
    symbol_chain = commodity.SymbolChain(page_property['chain_id'], page_property['chain_name'], json_file)
    page_property['symbol_chain'] = symbol_chain
    symbol_j = commodity.SymbolData('J', '焦炭', json_file)
    symbol_i = commodity.SymbolData('I', '铁矿石', json_file)
    symbol_chain.add_symbol(symbol)
    symbol_chain.add_symbol(symbol_j)
    symbol_chain.add_symbol(symbol_i)
    symbol_chain.initialize_data(dws)
    symbol.get_spot_months()
    df_profit = symbol.get_profits(symbol_chain)    
    df_term = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'], symbol.id)
    df_term['date'] = pd.to_datetime(df_term['date'])
    page_property['term_data']= df_term

# 基本面分析配置面板
main_chart_config =dbc.Accordion(
    [
        dbc.AccordionItem(
            [                
                dbc.Label('选择分析指标：', color='darkblue'),
                dbc.Checklist(
                    options=['基差率', '库存', '仓单', '持仓量', '库存消费比', '库存+仓单', '现货利润', '盘面利润', '现货利润+盘面利润'],
                    value=['基差率', '库存', '仓单', '持仓量', '现货利润'],
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
                    value=['基差率', '库存历史时间分位'],
                    id='select_synchronize_index', inline=True                    
                ),
                html.Hr(),
                dbc.Label('历史分位回溯时间：', color='darkblue'),
                dcc.Slider(
                    0, 130, value=36, step=None,
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
            # 期限结构分析图表
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [
                        html.Div(
                            [
                                # html.P(id='figure-click-output'),
                                dcc.Graph(figure={}, id='term-figure-placeholder'),    
                            ])
                        ]
                    ),
                    className="mt-3",
                )
            ),
            # 跨期分析图表
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(figure={}, id='intertemporal-figure-placeholder'),
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
    Input('look_forward_months', 'value'),
    allow_duplicate=True
)
def update_graph(select_index_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value):   
    symbol = page_property['symbol']
    if symbol.name not in page_property['chart_setting']:
        page_property['chart_setting'][symbol.name] = {}
        # initial_data()
        page_property['symbol_figure'] = commodity.SymbolFigure(symbol)
    figure = page_property['symbol_figure'].create_figure(select_index_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value)
    return figure

def display_term_structure_figure(click_date, spot_price):
        df_term = page_property['term_data']
        symbol = page_property['symbol']
        if df_term.empty:
             return None, None
        df_term = df_term[df_term['date']==click_date]
        max_open_interest_index= df_term['open_interest'].idxmax()
        domain_contract = df_term.loc[max_open_interest_index]['symbol']
        df_term = df_term.loc[max_open_interest_index:]
        dominant_months = symbol.symbol_setting['DominantMonths']
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        df_dominant_contract = df_term[df_term['交割月'].isin(dominant_months)]
        diff = df_dominant_contract['settle'].head(len(dominant_months)).diff().dropna()
        if all(diff>0):
            color_flag = 'rgba(0,255,0,0.5)'
        elif all(diff<0):
             color_flag = 'rgba(255,0,0,0.5)'
        else:
            color_flag = 'rgba(128,128,128,0.5)'
        
        spot_row = pd.DataFrame({
            'symbol': ['现货'],
            'close': [spot_price],
            'settle': [spot_price]
        })
        df_term = pd.concat([spot_row, df_term])
        # print(click_date, type(click_date),  df_term)
        # spot_figure =go.Scatter(x=spot_row['symbol'], y=spot_row['settle'], stackgroup='one',mode='markers',
                                # fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.2)',
                                # marker=dict(color='rgb(0, 123, 255)', opacity=1))
        future_figure = go.Scatter(x=df_dominant_contract['symbol'], y=df_dominant_contract['settle'], stackgroup='one', mode='markers',
                                             fill='tozeroy', fillcolor=color_flag,
                                             marker=dict(color=color_flag))
        term_fig = go.Figure()
        # term_fig.add_trace(spot_figure)
        term_fig.add_trace(future_figure)
        max_y = df_term['settle'].max() * 1.03
        min_y = df_term['settle'].min() * 0.97        
        current_date = click_date.strftime('%Y-%m-%d')
        # term_fig.add_hline(y=spot_price)
        term_fig.update_layout(yaxis_range=[min_y,max_y],
                               title='期限结构:'+current_date,
                               height=150,
                               margin=dict(l=0, r=0, t=30, b=0),
                               plot_bgcolor='WhiteSmoke',                   
                               showlegend=False)
        term_fig.update_xaxes(showgrid=False)
        term_fig.update_yaxes(showgrid=False)
        return term_fig, df_dominant_contract

def display_cross_term_figure(click_date, domain_contract):
    df_term = page_property['term_data']
    fig_rows = len(domain_contract)
    specs = [[{"secondary_y": True}] for _ in range(fig_rows)]
    row_widths = [0.1] * (fig_rows - 1) + [0.5]
    subtitles = ['跨期分析'] + list(domain_contract['symbol'][1:])
    colors = ['rgba(239,181,59,1.0)', 'rgba(84,134,240,0.5)', 'rgba(105,206,159,0.5)']
    cross_term_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.04)
    # cross_term_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, shared_xaxes=True, vertical_spacing=0.02)
    row = 1
    df_multi_term = pd.DataFrame()
    for symbol_name in domain_contract['symbol']:
        df = df_term[df_term['symbol']==symbol_name][['date', 'close']]
        symbol_figure = go.Scatter(x=df['date'], y=df['close'], name=symbol_name, marker_color=colors[row-1])
        cross_term_figure.add_trace(symbol_figure, row=1, col=1)
        df.rename(columns={'close': symbol_name}, inplace=True)
        if df_multi_term.empty:
            df_multi_term = df
            near_contract = symbol_name
        else:
            df_multi_term = pd.merge(df_multi_term, df, on='date', how='outer')
            df_multi_term['与'+symbol_name+'价差'] = df_multi_term[near_contract] - df_multi_term[symbol_name]
            sub_figure = go.Bar(x=df_multi_term['date'], y=df_multi_term['与'+symbol_name+'价差'], name=symbol_name+'价差', marker=dict(color=colors[row-1]))
            cross_term_figure.add_trace(sub_figure,row=row,col=1)
        row = row+1
    # df_multi_term = reduce(lambda left,right: pd.merge(left,right,on='date', how='outer'), data_frames)

    half_year_later = click_date + timedelta(days=180)
    date_now = datetime.now()
    end_date = half_year_later if date_now>half_year_later else date_now
    start_date = click_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    main_figure = page_property['symbol_figure']
    cross_term_figure.update_layout(
                                    height=500,
                                    margin=dict(l=0, r=0, t=20, b=0),
                                    plot_bgcolor='WhiteSmoke',     
                                    hovermode='x unified',              
                                    showlegend=False)
    cross_term_figure.update_xaxes(showgrid=False,
                                   dtick="M1",
                                   ticklabelmode="instant",   # instant  period
                                   tickformat="%m\n%Y",
                                   rangebreaks=[dict(values=main_figure.trade_breaks)],
                                   range=[start_date, end_date],)
    cross_term_figure.update_yaxes(showgrid=False)
    return cross_term_figure

@app.callback(
    # Output('figure-click-output', 'children'),
    Output('term-figure-placeholder', 'figure'),
    Output('intertemporal-figure-placeholder', 'figure'),
    Input('main-figure-placeholder', 'clickData'),
    allow_duplicate=True)
def display_click_data(clickData):
    if clickData is not None:
        # 获取第一个被点击的点的信息
        point_data = clickData['points'][0]
        # print(clickData['points'][1], clickData['points'][2])
        # 获取x轴坐标
        display_date = point_data['x']
        click_date = datetime.strptime(display_date, '%Y-%m-%d')
        spot_price = point_data['y']
        term_fig, df_dominant_contract = display_term_structure_figure(click_date, spot_price)
        cross_term_figure = display_cross_term_figure(click_date, df_dominant_contract)
        return term_fig, cross_term_figure
    else:
        return {}, {}

if __name__ == "__main__":
    initial_data()
    app.run_server(debug=True)
