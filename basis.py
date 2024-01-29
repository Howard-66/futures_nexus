import dash
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

page_property = {
    'dataworks': {},
    'symbol_id': 'RB',
    'symbol_name': '螺纹钢',
    'chain_id': 'steel',
    'chain_name': '黑色金属',
    'symbol': {},
    'symbol_chain': {},
    'symbol_figure': {},
    'chart_setting': {},
    'term_data': {},
}

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
                dbc.Label('选择期货价格类型：', color='darkblue'),
                dbc.RadioItems(
                    options=[
                        {"label": "主力合约收盘价", "value": '主力合约收盘价'},
                        {"label": "主力合约结算价", "value": '主力合约结算价'},
                        {"label": "近月合约收盘价", "value": '近月合约收盘价'},
                        {"label": "近月合约结算价", "value": '近月合约结算价'},
                    ],
                    value='近月合约收盘价',
                    id="radio_future_price", inline=True
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

analyzing_log = html.Div([
    dbc.Label('量化分析标签', color='darkblue'),
    html.Div(
        html.Span(
            id='html_analyzing_tags'
        ),    
    ),
    html.Hr(),
    dbc.Label('盈利-风险测算', color='darkblue'),
    # dbc.RadioItems(
    #     options=[
    #         {"label": "单边/跨期做多", "value": '单边/跨期做多'},
    #         {"label": "单边/跨期做空", "value": '单边/跨期做空'},
    #     ],
    #     value='单边/跨期做多',
    #     id="radio_trade_type", inline=True
    # ),       
    html.Div(id='html_profit_loss'),
    html.Hr(),
    dbc.Label('综合分析', color='darkblue'),
    dbc.Textarea(className="mb-3", placeholder="分析结论", id='txt_log_conclusion'),
    html.Div([
        dbc.Button("删除", color="danger", className="me-1", id='bt_log_delete'),
        dbc.Button("保存", color="success", className="me-1", id='bt_log_save'),
    ])
])

multi_charts = html.Div([
    dbc.Row([
        # 左侧面板
        dbc.Col([
            # 配置面板
            dbc.Row(dbc.Form(main_chart_config)),
            # 图表面板
            dbc.Row(
                dcc.Graph(figure={}, id='main-figure-placeholder'),    
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
            ),
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [                            
                            dbc.Form(analyzing_log),
                        ]
                    ),
                    className="mt-3",
                )                
            )
        ], width=3)
    ])
])

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            
        ]
    ),
    className="mt-3",
)

# 产业链下具体品种分析页面

tab_symbol_rb= dbc.Card(
    dbc.CardBody(
        [
            multi_charts
        ]
    ),
    className="mt-3",
)

# 产业链分析tabview
chain_tabs = dbc.Tabs(
    [
        # dbc.Tab(tab_main, label="基本面分析", tab_id="tab-main"),
        dbc.Tab(tab2_content, label="产业链", tab_id="tab-overview"),
        dbc.Tab(tab_symbol_rb, label="螺纹钢", tab_id="tab-symbol-rb"),
        dbc.Tab(tab2_content, label="铁矿石", tab_id="tab-symbol-i"),
        dbc.Tab(tab2_content, label="焦炭", tab_id="tab-symbol-l"),
    ],
    id="tabs-chain",
    active_tab="tab-overview",
)        

page_layout = html.Div(
    [
        chain_tabs,
    ],
)

preivouse_input = {'selected_index': [], 
                   'previous_maker': [], 
                   'previouse_sync_index': [],
                   'previouse_look_forward_months': 0
}

def layout():
    return page_layout

# 初始化数据
def initialize():
    dws = dataworks.DataWorks()
    page_property['dataworks'] = dws
    symbol = commodity.SymbolData(page_property['symbol_id'], page_property['symbol_name'])
    page_property['symbol'] = symbol
    symbol_chain = commodity.SymbolChain(page_property['chain_id'], page_property['chain_name'])
    page_property['symbol_chain'] = symbol_chain
    symbol_j = commodity.SymbolData('J', '焦炭')
    symbol_i = commodity.SymbolData('I', '铁矿石')
    symbol_chain.add_symbol(symbol)
    symbol_chain.add_symbol(symbol_j)
    symbol_chain.add_symbol(symbol_i)
    symbol_chain.initialize_data(dws)
    symbol.get_spot_months()
    df_term = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
    df_term['date'] = pd.to_datetime(df_term['date'])
    page_property['term_data']= df_term
    page_property['symbol_figure'] = commodity.SymbolFigure(symbol)

# Add controls to build the interaction
@callback(
    Output(component_id='main-figure-placeholder', component_property='figure'),
    Input('select_index', 'value'),
    Input('radio_future_price', 'value'),
    Input('switch_marker', 'value'),
    Input('select_synchronize_index', 'value'),
    Input('look_forward_months', 'value'),
    # allow_duplicate=True
)
def update_graph(select_index_value, radio_future_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value):   
    print('on_update_graph')
    symbol = page_property['symbol']
    if symbol.name not in page_property['chart_setting']:
        page_property['chart_setting'][symbol.name] = {}
        # initial_data()
        # page_property['symbol_figure'] = commodity.SymbolFigure(symbol)
    symbol_chain = page_property['symbol_chain']
    df_profit = symbol.get_profits(radio_future_value, symbol_chain)    
    figure = page_property['symbol_figure'].create_figure(select_index_value, radio_future_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value)
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
        df_term = df_term[df_term['交割月'].isin(dominant_months)]
        spot_row = pd.DataFrame({
            'symbol': ['现货'],
            'close': [spot_price],
            'settle': [spot_price]
        })
        df_dominant_contract = pd.concat([spot_row, df_term])        
        diff = df_dominant_contract['settle'].head(len(dominant_months)+1).diff().dropna()
        if all(diff>0):
            color_flag = 'rgba(0,255,0,0.5)'
            trade_flag = 'Short'
        elif all(diff<0):
             color_flag = 'rgba(255,0,0,0.5)'
             trade_flag = 'Long'
        else:
            color_flag = 'rgba(128,128,128,0.5)'
            trade_flag = 'X'
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
        max_y = df_dominant_contract['settle'].max() * 1.01
        min_y = df_dominant_contract['settle'].min() * 0.99        
        current_date = click_date.strftime('%Y-%m-%d')
        # term_fig.add_hline(y=spot_price)
        term_fig.update_layout(yaxis_range=[min_y,max_y],
                               title='期限结构:'+current_date,
                               height=120,
                               margin=dict(l=0, r=0, t=30, b=0),
                               plot_bgcolor='WhiteSmoke',                   
                               showlegend=False)
        term_fig.update_xaxes(showgrid=False)
        term_fig.update_yaxes(showgrid=False)
        return term_fig, df_term, trade_flag

def display_cross_term_figure(click_date, domain_contract):
    half_year_later = click_date + timedelta(days=180)
    date_now = datetime.now()
    end_date = half_year_later if date_now>half_year_later else date_now
    start_date = click_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')    
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
    profit_loss = {}
    for symbol_name in domain_contract['symbol']:
        df = df_term[df_term['symbol']==symbol_name][['date', 'close']]
        delivery_date = df['date'].max()    
        last_trading_day = delivery_date.replace(day=1)                
        symbol_figure = go.Scatter(x=df['date'], y=df['close'], name=symbol_name, marker_color=colors[row-1])
        cross_term_figure.add_trace(symbol_figure, row=1, col=1)
        df.rename(columns={'close': symbol_name}, inplace=True)
        df_trading = df[(df['date']>= click_date) & (df['date']<=last_trading_day)]
        if df_multi_term.empty:
            entry_price = df_trading.loc[df_trading['date']==click_date][symbol_name].iloc[0]
            # print('Open Price: ', entry_price)            
            df_multi_term = df
            near_contract = symbol_name            
            max_id = df_trading[symbol_name].idxmax()
            max_diff = df_trading.loc[max_id][symbol_name] - entry_price
            max_date = df_trading.loc[max_id]['date']
            max_date_diff = max_date - click_date
            # print('Max: ', max_id, max_diff, max_date)
            min_id = df_trading[symbol_name].idxmin()
            min_diff = entry_price - df_trading.loc[min_id][symbol_name]
            min_date = df_trading.loc[min_id]['date']
            min_date_diff = min_date - click_date
            # print('Min: ', min_id, min_diff, min_date)
            profit_loss[symbol_name+'单边'] = {'多头':{'点差': max_diff, '%': max_diff/entry_price, '持续时间': max_date_diff.days},
                                  '空头':{'点差': min_diff, '%': min_diff/entry_price, '持续时间': min_date_diff.days}}
        else:       
            df_multi_term = pd.merge(df_multi_term, df, on='date', how='outer')
            df_multi_term[symbol_name+'价差'] = df_multi_term[near_contract] - df_multi_term[symbol_name]
            sub_figure = go.Bar(x=df_multi_term['date'], y=df_multi_term[symbol_name+'价差'], name=symbol_name+'价差', marker=dict(color=colors[row-1]))
            cross_term_figure.add_trace(sub_figure,row=row,col=1)
            df_trading = df_multi_term[(df_multi_term['date']>= click_date) & (df_multi_term['date']<=last_trading_day)]
            entry_price_diff = df_trading.loc[df_trading['date']==click_date][symbol_name+'价差'].iloc[0]
            max_id = df_trading[symbol_name+'价差'].idxmax()
            max_price = df_trading.loc[max_id][symbol_name+'价差']
            max_diff =  max_price - entry_price_diff
            max_date = df_trading.loc[max_id]['date']
            # print('Max: ', max_id, max_price, max_diff, max_date)
            min_id = df_trading[symbol_name+'价差'].idxmin()
            min_price = df_trading.loc[min_id][symbol_name+'价差']
            min_diff = entry_price_diff - min_price
            min_date = df_trading.loc[min_id]['date']
            # print('Min: ', min_id, min_price, min_diff, min_date)
            profit_loss[symbol_name+'套利'] = {'多头':{'点差': max_diff, '%': max_diff/entry_price/2, '持续时间': (max_date - click_date).days},
                                                '空头':{'点差': min_diff, '%': min_diff/entry_price/2, '持续时间': (min_date - click_date).days}}              
        row = row+1        
    # df_multi_term = reduce(lambda left,right: pd.merge(left,right,on='date', how='outer'), data_frames)
    main_figure = page_property['symbol_figure']
    filtered_data = df_term[(df_term['date'] >= start_date) & (df_term['date'] <= end_date)]
    # 计算 y 轴的最大值和最小值
    max_y = filtered_data['close'].max()*1.01
    min_y = filtered_data['close'].min()*0.99
    cross_term_figure.update_layout(
                                    height=400,
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
    cross_term_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
    return cross_term_figure, profit_loss
    
@app.callback(
    # Output('figure-click-output', 'children'),
    Output('term-figure-placeholder', 'figure'),
    Output('intertemporal-figure-placeholder', 'figure'),
    # Output('radio_trade_type', 'value'),
    Output('html_analyzing_tags', 'children'),
    Output('html_profit_loss', 'children'),
    # Output('log_basis', 'color'),
    # Output('log_term_structure', 'color'),
    # Output('log_inventory', 'color'),
    # Output('log_receipt', 'color'),
    # Output('log_open_interest', 'color'),
    # Output('log_spot_profit', 'color'),
    # Output('log_future_profit', 'color'),
    Input('main-figure-placeholder', 'clickData'),
    allow_duplicate=True)
def display_click_data(clickData):
    if clickData is not None:
        # 获取第一个被点击的点的信息
        point_data = clickData['points'][0]
        # 获取x轴坐标
        display_date = point_data['x']
        click_date = datetime.strptime(display_date, '%Y-%m-%d')
        spot_price = point_data['y']
        # 绘制期限结构视图
        term_fig, df_dominant_contract, term_flag = display_term_structure_figure(click_date, spot_price)
        # 绘制跨期套利分析视图
        cross_term_figure, profit_loss = display_cross_term_figure(click_date, df_dominant_contract)
        # print(profit_loss)
        # 准备分析日志数据
        flag_color ={'Long': 'danger', 'Short': 'success', 'X': 'dark'}
        flag_color2 ={'red': 'danger', 'green': 'success', 'gray': 'dark'}        
        trade_type = {'Long': '单边/跨期做多', 'Short': '单边/跨期做空'}
        symbol = page_property['symbol']
        basis = clickData['points'][2]['y']
        basis_flag = 'Long' if basis>0 else 'Short'
        click_data = symbol.data_rank[symbol.data_rank['date']==click_date]
        inventory_flag = click_data['库存分位颜色'].iloc[0]
        receipt_flag = click_data['仓单分位颜色'].iloc[0]
        openinterest_flag = click_data['持仓量分位颜色'].iloc[0]
        spotprofit_flag = click_data['现货利润分位颜色'].iloc[0]
        futureprofit_flag = click_data['盘面利润分位颜色'].iloc[0]
        html_analyzing_tags =[
            #     dbc.Badge("远月/近月/交割月", color="primary", className="me-1",id='log_period'),
            #     html.Span(" | "),
                dbc.Badge("基差", color=flag_color[basis_flag], className="me-1", id='log_basis'),
                dbc.Badge("期限结构", color=flag_color[term_flag], className="me-1", id='log_term_structure'),
                html.Span(" | "),
                dbc.Badge("库存", color=flag_color2[inventory_flag], className="me-1", id='log_inventory'),
                dbc.Badge("仓单", color=flag_color2[receipt_flag], className="me-1", id='log_receipt'),
                dbc.Badge("持仓量", color=flag_color2[openinterest_flag], className="me-1", id='log_open_interest'),
                html.Span(" | "),
                dbc.Badge("现货利润", color=flag_color2[spotprofit_flag], className="me-1", id='log_spot_profit'),
                dbc.Badge("盘面利润", color=flag_color2[futureprofit_flag], className="me-1", id='log_future_profit'),
        ]
        strategy = []
        direction = []
        point_diff =[]
        percent = []
        duration = []
        for key, value in profit_loss.items():
            strategy.append(key)
            strategy.append('')
            for key2, value2 in value.items():
                direction.append(key2)
                point_diff.append(value2['点差'])
                percent.append(format(value2['%']*100, '.2f'))
                duration.append(value2['持续时间'])
            
        df = pd.DataFrame(
            {
                "策略": strategy,
                "方向": direction,
                "点差": point_diff,
                "%": percent,
                "周期": duration,
            }
        )        
        html_profit_loss = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        return term_fig, cross_term_figure, html_analyzing_tags, html_profit_loss
        # return term_fig, cross_term_figure, trade_type[basis_flag], flag_color[basis_flag], flag_color[term_flag], flag_color2[inventory_flag], flag_color2[receipt_flag], flag_color2[openinterest_flag], flag_color2[spotprofit_flag], flag_color2[futureprofit_flag], 
    else:
        return {}, {}, {}, {}
        # return {}, {}, '', 'dark', 'dark', 'dark', 'dark', 'dark', 'dark', 'dark'

@app.callback(
    Output(component_id='main-figure-placeholder', component_property='figure', allow_duplicate=True),
    Input('main-figure-placeholder', 'relayoutData')
)
def display_relayout_data(relayoutData):
    # if 'symbol_figure' not in page_property:
    #     return dash.no_update
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        xaxis_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        main_figure = page_property['symbol_figure'].update_yaxes(xaxis_range)
        return main_figure
    else:
        return dash.no_update

