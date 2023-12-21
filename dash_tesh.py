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
global_vars = {
    'trade_date': []
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
    # merged_data = symbol.merge_data()
    # # 生成上由原材料的现货和期货价格数据
    # symbol_j = commodity.SymbolData('J', '焦炭', json_file)
    # symbol_j.merge_data()
    # symbol_i = commodity.SymbolData('I', '铁矿石', json_file)
    # symbol_i.merge_data()
    # profit_j = symbol_j.symbol_data[['日期', '现货价格', '主力合约结算价']].copy()
    # profit_j.rename(columns={'现货价格': symbol_j.name+'现货', '主力合约结算价': symbol_j.name+'期货'}, inplace=True)
    # profit_i = symbol_i.symbol_data[['日期', '现货价格', '主力合约结算价']].copy()
    # profit_i.rename(columns={'现货价格': symbol_i.name+'现货', '主力合约结算价': symbol_i.name+'期货'}, inplace=True)
    # # 计算品种的现货利润和盘面利润
    # formula = symbol.symbol_setting['ProfitFormula']
    # df_profit = pd.merge(profit_j, profit_i, on='日期', how='outer')
    # # df_profit = pd.merge(symbol.symbol_data[['日期', '现货价格', '主力合约结算价']], df_profit, on='日期', how='outer').dropna(axis=0, how='all', subset=['现货价格', '主力合约结算价'])
    # df_profit = pd.merge(symbol.symbol_data[['日期', '现货价格', '主力合约结算价']], df_profit, on='日期', how='outer')
    # df_profit['现货利润'] = df_profit['现货价格'] - formula['Factor'][symbol_j.name] * df_profit[symbol_j.name+'现货'] - formula['Factor'][symbol_i.name] * df_profit[symbol_i.name+'现货'] - formula['其他成本']
    # df_profit['盘面利润'] = df_profit['主力合约结算价'] - formula['Factor'][symbol_j.name] * df_profit[symbol_j.name+'期货'] - formula['Factor'][symbol_i.name] * df_profit[symbol_i.name+'期货'] - formula['其他成本']
    # df_profit.dropna(axis=0, how='all', subset=['现货利润', '盘面利润'], inplace=True)
    # df_append = df_profit[['日期', '现货利润', '盘面利润']].copy()
    # symbol.symbol_data = pd.merge(symbol.symbol_data, df_append, on='日期', how='outer')
    global_vars['trade_date'] = ak.tool_trade_date_hist_sina()['trade_date']

# # 主图全局变量
main_figure = {}
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
                    id='select_index',
                    inline=True
                ),
                html.Hr(),
                dbc.Label('标记区间：', color='darkblue'),
                dbc.Checklist(
                    options=['现货交易月', '指标共振周期'],
                    value=['现货交易月', '指标共振周期'],
                    id='switch_marker',
                    switch=True,
                    inline=True
                ),
                html.Hr(),
                dbc.Label('共振指标设置：', color='darkblue'),
                dbc.Checklist(                    
                    options=['基差率', '库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位', '库存|仓单', '现货利润|盘面利润'],
                    value=['基差率', '库存|仓单', '现货利润|盘面利润'],
                    id='select_synchronize_index',
                    inline=True                    
                ),
                html.Hr(),
                dbc.Label('历史分位回溯时间：', color='darkblue'),
                dcc.Slider(
                    0, 130, value=60,
                    step=None,
                    marks={
                        6: '6个月',
                        12: '1年',
                        24: '2年',
                        36: '3年',
                        60: '5年',
                        120: '10年',
                        130: {'label': 'All', 'style': {'color': 'darkblue'}}
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
                        dcc.Graph(figure={}, id='graph-placeholder'),    
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
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='select_index', component_property='value'),
    Input('switch_marker', 'value'),
    Input('select_synchronize_index', 'value'),
    Input('look_forward_months', 'value')
)
def update_graph(select_index_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value):    
    if symbol_name not in charts_setting_dict:
        charts_setting_dict[symbol_name] = {}
        initial_data()
    # symbol = symbol_chain.get_symbol(symbol_name)
    if look_forward_months_value != preivouse_input['previouse_look_forward_months']:
        symbol.calculate_data_rank(trace_back_months=look_forward_months_value)
        
    fig_rows = len(select_index_value) + 1
    specs = [[{"secondary_y": True}] for _ in range(fig_rows)]
    row_widths = [0.1] * (fig_rows - 1) + [0.5]
    subtitles = ['现货/期货价格'] + select_index_value
    main_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.02)
    # 创建主图：期货价格、现货价格、基差
    fig_future_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['主力合约收盘价'], name='期货价格', 
                                marker_color='rgb(84,134,240)')
    fig_spot_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgb(105,206,159)')
    fig_basis = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', 
                        marker=dict(color='rgb(239,181,59)', opacity=0.4), showlegend=False)
    main_figure.add_trace(fig_basis, secondary_y=True)
    main_figure.add_trace(fig_future_price, row = 1, col = 1)
    main_figure.add_trace(fig_spot_price, row = 1, col = 1)
    print(select_index_value, switch_marker_value)

    main_figure.data = main_figure.data[:3]
    sub_index_rows = 2
    # 创建副图-基差率，并根据基差率正负配色
    key_basis_rate = '基差率'
    if key_basis_rate in select_index_value:
        sign_color_mapping = {0:'green', 1:'red'}
        fig_basis_rate = go.Bar(x=symbol.symbol_data['日期'], y = symbol.symbol_data['基差率'], name=key_basis_rate,
                                marker=dict(color=symbol.basis_color['基差率颜色'], colorscale=list(sign_color_mapping.values()),
                                            showscale=False),
                                showlegend=False,
                                hovertemplate='%{y:.2%}')
        main_figure.add_trace(fig_basis_rate, row = sub_index_rows, col = 1)
        sub_index_rows = sub_index_rows + 1

    histroy_color_mapping ={1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'}
    # 创建副图-库存
    key_storage = '库存'
    if key_storage in select_index_value:
        fig_storage = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name=key_storage, marker_color='rgb(239,181,59)', showlegend=False,)
        # fig_storage = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name='库存', mode='markers', marker=dict(size=2, color='rgb(239,181,59)'))
        symbol.data_rank['库存分位颜色'] = symbol.data_rank['库存历史时间分位'].map(histroy_color_mapping)
        # fig_storage_rank = go.Bar(x=df_rank['日期'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color='rgb(234,69,70)')
        fig_storage_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['库存历史时间百分位'], name='库存分位', 
                                marker=dict(color=symbol.data_rank['库存分位颜色'], opacity=0.6),
                                showlegend=False,
                                hovertemplate='%{y:.2%}')
        main_figure.add_trace(fig_storage_rank, row = sub_index_rows, col = 1, secondary_y=True)
        main_figure.add_trace(fig_storage, row = sub_index_rows, col = 1)
        sub_index_rows = sub_index_rows + 1

    # 创建副图-仓单
    key_receipt = '仓单'
    if key_receipt in select_index_value:
        fig_receipt = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['仓单'], name=key_receipt, marker_color='rgb(239,181,59)', showlegend=False,)
        # symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
        # fig_receipt_rank = go.Scatter(x=symbol.data_rank['日期'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位', marker_color='rgb(239,181,59)')
        symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
        fig_receipt_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位',
                                    marker=dict(color=symbol.data_rank['仓单分位颜色'], opacity=0.6),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
        main_figure.add_trace(fig_receipt_rank, row = sub_index_rows, col = 1, secondary_y=True)
        main_figure.add_trace(fig_receipt, row = sub_index_rows, col = 1)
        sub_index_rows = sub_index_rows + 1

    # 创建副图-现货利润
    key_spot_profit = '现货利润'
    if key_spot_profit in select_index_value:
        # fig_spot_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货利润'], name='现货利润', mode='markers', marker=dict(size=2, color='rgb(234,69,70)'))
        fig_spot_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货利润'], name=key_spot_profit, marker_color='rgb(239,181,59)', showlegend=False,)
        symbol.data_rank['现货利润分位颜色'] = symbol.data_rank['现货利润历史时间分位'].map(histroy_color_mapping)
        fig_spot_profit_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['现货利润历史时间百分位'], name='现货利润', 
                                    marker=dict(color=symbol.data_rank['现货利润分位颜色'], opacity=0.6),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
        main_figure.add_trace(fig_spot_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
        main_figure.add_trace(fig_spot_profit, row = sub_index_rows, col = 1)
        sub_index_rows = sub_index_rows + 1

    # 创建副图-盘面利润
    key_future_profit = '盘面利润'
    if key_future_profit in select_index_value:
        fig_future_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['盘面利润'], name=key_future_profit, marker_color='rgb(239,181,59)', showlegend=False,)
        symbol.data_rank['盘面利润分位颜色'] = symbol.data_rank['盘面利润历史时间分位'].map(histroy_color_mapping)
        fig_future_profit_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['盘面利润历史时间百分位'], name='盘面利润 ', 
                                        marker=dict(color=symbol.data_rank['盘面利润分位颜色'], opacity=0.6),
                                        showlegend=False,
                                        hovertemplate='%{y:.2%}')
        main_figure.add_trace(fig_future_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
        main_figure.add_trace(fig_future_profit, row = sub_index_rows, col = 1)
        sub_index_rows = sub_index_rows + 1

    # 根据交易时间过滤空数据
    trade_date = [d.strftime("%Y-%m-%d") for d in global_vars['trade_date']]
    dt_all = pd.date_range(start=symbol.symbol_data['日期'].iloc[0],end=symbol.symbol_data['日期'].iloc[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(trade_date))
    global_vars['breaks'] = dt_breaks

    # 用浅蓝色背景标记现货月时间范围
    key_mark_spot_months = '现货交易月'
    key_mark_sync_index = '指标共振周期'
    if key_mark_spot_months in switch_marker_value or key_mark_sync_index in switch_marker_value:
        main_figure.update_layout(shapes=[])
    if key_mark_spot_months in switch_marker_value:        
        for _, row in symbol.spot_months.iterrows():
            main_figure.add_shape(
                # 矩形
                type="rect",
                x0=row['Start Date'], x1=row['End Date'],
                y0=0, y1=1,
                xref='x', yref='paper',
                fillcolor="LightBlue", opacity=0.1,
                line_width=0,
                layer="below"
            )
    else:
        # shapes = main_figure.layout.shapes
        # shapes[0]['line']['width'] = 0
        main_figure.update_layout(shapes=[])

    if key_mark_sync_index in switch_marker_value:
        print(select_synchronize_index_value)
        df_signals =symbol.get_signals(select_synchronize_index_value)
        signal_nums = len(select_synchronize_index_value)
        df_short_signals = df_signals[df_signals['信号数量']==-signal_nums]        
        for _, row in df_short_signals.iterrows():
            next_day = row['日期'] + timedelta(days=1)
            main_figure.add_shape(
                type='circle',
                x0=row['日期'], x1=next_day,
                y0=1, y1=0.997,
                xref='x', yref='paper',
                fillcolor='green',
                line_color='green'
            )            
        df_long_signals = df_signals[df_signals['信号数量']==signal_nums]        
        for _, row in df_long_signals.iterrows():
            next_day = row['日期'] + timedelta(days=1)
            main_figure.add_shape(
                type='circle',
                x0=row['日期'], x1=next_day,
                y0=1, y1=0.997,
                xref='x', yref='paper',
                fillcolor='red',
                line_color='red'
            )
    # 图表初始加载时，显示最近一年的数据
    one_year_ago = datetime.now() - timedelta(days=365)
    date_now = datetime.now().strftime('%Y-%m-%d')
    date_one_year_ago = one_year_ago.strftime('%Y-%m-%d')
    # X轴坐标按照年-月显示
    main_figure.update_xaxes(
        showgrid=False,
        zeroline=True,
        dtick="M1",  # 按月显示
        ticklabelmode="instant",   # instant  period
        tickformat="%m\n%Y",
        rangebreaks=[dict(values=dt_breaks)],
        rangeslider_visible = False, # 下方滑动条缩放
        range=[date_one_year_ago, date_now],
        # 增加固定范围选择
        rangeselector = dict(
            buttons = list([
                dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
                dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
                # dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),                
                dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
                dict(step = 'all')
                ]))
    )
    main_figure.update_yaxes(
        showgrid=False,
    )
    #main_figure.update_traces(xbins_size="M1")
    max_y = symbol.symbol_data['主力合约收盘价'] .max() * 1.05
    min_y = symbol.symbol_data['主力合约收盘价'] .min() * 0.95
    main_figure.update_layout(
        yaxis_range=[min_y,max_y],
        #autosize=False,
        #width=800,
        height=1200,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='WhiteSmoke',  
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0,
            bgcolor='WhiteSmoke',
            bordercolor='LightSteelBlue',
            borderwidth=1
        )
    )
    preivouse_input['previouse_look_forward_months'] = look_forward_months_value
    return main_figure

@app.callback(
    Output('figure-click-output', 'children'),
    Input('graph-placeholder', 'clickData'))
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
    app.run_server(debug=True)
