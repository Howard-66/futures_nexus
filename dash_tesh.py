import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import commodity
import akshare as ak

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

main_chart_config =dbc.Accordion(
    [
        dbc.AccordionItem(
            [
                dbc.Label('选择指标分析组合：', color='darkblue'),
                dbc.Select(
                    options=['基差-库存/仓单', '基差-库存-现货利润', '基差-库存/仓单-现货利润/盘面利润', '基差-库存效费比-现货利润',
                             '基差-库存/仓单-现货利润/盘面利润历史分位'],
                    value='基差-库存/仓单-现货利润/盘面利润历史分位',
                    id='select_index_group',
                ),
                html.Hr(),
                dbc.Label('选择分析指标：', color='darkblue'),
                dbc.Checklist(
                    options=['基差率', '库存/仓单', '库存消费比', '库存/仓单-历史百分位', '现货利润/盘面利润','现货利润/盘面利润-历史百分位' ],
                    value=['基差率', '库存/仓单-历史百分位', '现货利润/盘面利润-历史百分位'],
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
                    options=['基差率', '库存', '库存-历史分位', '仓单', '仓单-历史分位', '库存消费比', '现货利润', '现货利润-历史分位', '盘面利润', '盘面利润-历史分位'],
                    value=['基差率', '库存-历史分位', '现货利润-历史分位'],
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
                    id='look-forward-months'
                )
            ], 
        title='图表设置'),
    ],
    start_collapsed=True,
    # flush=True,
)

tab_main2 = html.Div([
    # 主框架
    dbc.Row([
        # 左侧面板
        dbc.Col([
            # 配置面板
            main_chart_config,
            # 图表面板
            dcc.Graph(figure={}, id='graph-placeholder'),    
        ], width=8),
        # 右侧面板
        dbc.Col([
            # 跨期分析图表
            dbc.Row(

            ),
            # 期限结构分析图表
            dbc.Row(

            )
        ], width=4)
    ])
])

tab_main = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dcc.Dropdown(
                                    ['基差', '基差率', '库存/仓单', '库存消费比', '库存/仓单-历史百分位', '现货利润/盘面利润','现货利润/盘面利润-历史百分位' ],
                                    ['基差', '基差率', '库存/仓单', '现货利润/盘面利润'],
                                    id='main_chart_dropdown',
                                    multi=True
                                ),              
                                # dcc.Graph(figure={}, id='graph-placeholder'),                                           
                            ]
                        ),
                        className="mt-3",
                    ),
                    width=8),
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.P("This is tab 2!", className="card-text"),
                                            dbc.Button("Don't click here", color="danger"),
                                        ]
                                    ),
                                    className="mt-3",
                                ),                                
                            ),
                            dbc.Row(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.P("This is tab 2!", className="card-text"),
                                            dbc.Button("Don't click here", color="danger"),
                                        ]
                                    ),
                                    className="mt-3",
                                ),
                            )
                        ],
                        width='4'
                    )
            ]
        )
    ]
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]
    ),
    className="mt-3",
)

app.layout = dbc.Container(
    dbc.Card(
        [
            dbc.CardHeader(
                html.P("FFA Demo", className="card-text")
            ),
            dbc.CardBody(
                dbc.Tabs(
                    [
                        dbc.Tab(tab_main2, label="Tab 1", tab_id="tab-1"),
                        dbc.Tab(tab_main, label="Tab 2", tab_id="tab-2"),
                    ],
                    id="card-tabs",
                    active_tab="tab-1",
                )
            ),
        ]
    ),
    className="p-5",
    fluid=True,
)



# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='main_chart_dropdown', component_property='value')
)
def update_graph(col_chosen):
    # 创建主品种数据
    symbol_id = 'RB'
    symbol_name = '螺纹钢'
    fBasePath = 'steel/data/mid-stream/螺纹钢/'
    json_file = './steel/setting.json'
    symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)
    merged_data = symbol.merge_data()
    # 生成上由原材料的现货和期货价格数据
    symbol_j = commodity.SymbolData('J', '焦炭', json_file)
    data_j = symbol_j.merge_data()
    symbol_i = commodity.SymbolData('I', '铁矿石', json_file)
    data_i = symbol_i.merge_data()
    profit_j = data_j[['日期', '现货价格', '主力合约结算价']].copy()
    profit_j.rename(columns={'现货价格': symbol_j.name+'现货', '主力合约结算价': symbol_j.name+'期货'}, inplace=True)
    profit_i = data_i[['日期', '现货价格', '主力合约结算价']].copy()
    profit_i.rename(columns={'现货价格': symbol_i.name+'现货', '主力合约结算价': symbol_i.name+'期货'}, inplace=True)
    # 计算品种的现货利润和盘面利润
    formula = symbol.symbol_setting['利润公式']
    df_profit = pd.merge(profit_j, profit_i, on='日期', how='outer')
    df_profit = pd.merge(merged_data[['日期', '现货价格', '主力合约结算价']], df_profit, on='日期', how='outer').dropna(axis=0, how='all', subset=['现货价格', '主力合约结算价'])
    df_profit['现货利润'] = df_profit['现货价格'] - formula[symbol_j.name] * df_profit[symbol_j.name+'现货'] - formula[symbol_j.name] * df_profit[symbol_i.name+'现货'] - formula['其他成本']
    df_profit['盘面利润'] = df_profit['主力合约结算价'] - formula[symbol_j.name] * df_profit[symbol_j.name+'期货'] - formula[symbol_i.name] * df_profit[symbol_i.name+'期货'] - formula['其他成本']
    df_profit.dropna(axis=0, how='all', subset=['现货利润', '盘面利润'], inplace=True)
    df_append = df_profit[['日期', '现货利润', '盘面利润']].copy()
    symbol.symbol_data = pd.merge(symbol.symbol_data, df_append, on='日期', how='outer')
    # 计算各指标的历史百分位和历史分位数据
    ranked_list = ['库存', '仓单', '现货利润', '盘面利润']
    df_rank = pd.DataFrame()
    for field in ranked_list:
        df_rank = symbol.history_time_ratio(field, df_rank, trace_back_months=60)
    # 创建基差-库存-利润分析图表
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                        specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]],
                    vertical_spacing=0.01, 
                    subplot_titles=('基差分析', '基差率', '库存/仓单历史分位', '现货利润/盘面利润'), 
                    row_width=[0.1, 0.1, 0.1, 0.7])

    # 创建主图：期货价格、现货价格、基差
    fig_future_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['主力合约收盘价'], name='期货价格', 
                                marker_color='rgb(84,134,240)')
    fig_spot_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgb(105,206,159)')
    fig_basis = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', 
                        marker_color='rgb(239,181,59)', showlegend=False)
    fig.add_trace(fig_basis, secondary_y=True)
    fig.add_trace(fig_future_price, row = 1, col = 1)
    fig.add_trace(fig_spot_price, row = 1, col = 1)

    # 创建辅图-基差率，并根据基差率正负配色
    sign_color_mapping = {0:'green', 1:'red'}
    df_figure = pd.DataFrame()
    df_figure['基差率颜色'] = symbol.symbol_data['基差率'] > 0
    df_figure['基差率颜色'] = df_figure['基差率颜色'].replace({True:1, False:0})
    fig_basis_rate = go.Bar(x=symbol.symbol_data['日期'], y = symbol.symbol_data['基差率'], name='基差率',
                            marker=dict(color=df_figure['基差率颜色'], colorscale=list(sign_color_mapping.values()),
                                        showscale=False),
                            showlegend=False,
                            hovertemplate='%{y:.2%}')
    fig.add_trace(fig_basis_rate, row = 2, col = 1)

    # 创建辅图-库存/仓单
    # fig_receipt = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['仓单'], name='仓单', marker_color='rgb(239,181,59)')
    # fig_storage = go.Bar(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name='库存', marker_color='rgb(234,69,70)')
    #fig_storage = px.bar(df_rb0, x='日期', y='库存')
    # fig.add_trace(fig_receipt, row = 3, col = 1, secondary_y=True)
    # fig.add_trace(fig_storage, row = 3, col = 1)

    # 创建辅图-库存/仓单历史时间百分位，并根据分位配色
    histroy_color_mapping ={1:'red', 2:'lightblue', 3:'lightblue', 4:'lightblue', 5:'green'}
    # df_rank['仓单分位颜色'] = df_rank['仓单历史时间分位'].map(histroy_color_mapping)
    # fig_receipt_rank = go.Scatter(x=df_rank['日期'], y=df_rank['仓单历史时间百分位'], name='仓单分位', marker_color='rgb(239,181,59)')
    fig_receipt_rank = go.Scatter(x=df_rank['日期'], y=df_rank['仓单历史时间百分位'], name='仓单分位', mode='markers',
                                marker=dict(size=2, color=df_rank['仓单历史时间分位'], colorscale=list(histroy_color_mapping.values())),
                                showlegend=False,
                                hovertemplate='%{y:.2%}')
    fig.add_trace(fig_receipt_rank, row = 3, col = 1, secondary_y=True)
    df_rank['库存分位颜色'] = df_rank['库存历史时间分位'].map(histroy_color_mapping)
    # fig_storage_rank = go.Bar(x=df_rank['日期'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color='rgb(234,69,70)')
    fig_storage_rank = go.Bar(x=df_rank['日期'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color=df_rank['库存分位颜色'],
                            hovertemplate='%{y:.2%}')
    fig.add_trace(fig_storage_rank, row = 3, col = 1)

    # 创建辅图-现货利润/盘面利润
    # fig_spot_profit = go.Scatter(x=df_profit['日期'], y=df_profit['现货利润'], name='现货利润', marker_color='rgb(239,181,59)')
    # fig_future_profit = go.Bar(x=df_profit['日期'], y=df_profit['盘面利润'], name='盘面利润', marker_color='rgb(234,69,70)')
    # fig.add_trace(fig_spot_profit, row = 4, col = 1, secondary_y=True)
    # fig.add_trace(fig_future_profit, row = 4, col = 1)

    # 创建辅图-现货利润/盘面利润历史时间分位
    df_rank['盘面利润分位颜色'] = df_rank['盘面利润历史时间分位'].map(histroy_color_mapping)
    fig_spot_profit = go.Scatter(x=df_rank['日期'], y=df_rank['现货利润历史时间百分位'], name='现货利润', mode='markers',
                                marker=dict(size=2, color=df_rank['现货利润历史时间分位'], colorscale=list(histroy_color_mapping.values())),
                                hovertemplate='%{y:.2%}')
    fig.add_trace(fig_spot_profit, row = 4, col = 1, secondary_y=True)
    fig_future_profit = go.Bar(x=df_rank['日期'], y=df_rank['盘面利润历史时间百分位'], name='盘面利润', marker_color=df_rank['盘面利润分位颜色'],
                            showlegend=False,
                            hovertemplate='%{y:.2%}')
    fig.add_trace(fig_future_profit, row = 4, col = 1)

    # 根据交易时间过滤空数据
    trade_date = ak.tool_trade_date_hist_sina()['trade_date']
    trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
    dt_all = pd.date_range(start=symbol.symbol_data['日期'].iloc[0],end=symbol.symbol_data['日期'].iloc[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(trade_date))

    # X轴坐标按照年-月显示
    fig.update_xaxes(
        showgrid=True,
        zeroline=True,
        dtick="M1",  # 按月显示
        ticklabelmode="period",   # instant  period
        tickformat="%b\n%Y",
        rangebreaks=[dict(values=dt_breaks)],
        rangeslider_visible = False, # 下方滑动条缩放
        # 增加固定范围选择
        # rangeselector = dict(
        #     buttons = list([
        #         dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
        #         dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
        #         dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
        #         dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
        #         dict(step = 'all')
        #         ]))
    )
    #fig.update_traces(xbins_size="M1")
    max_y = symbol.symbol_data['主力合约收盘价'] .max() * 1.05
    min_y = symbol.symbol_data['主力合约收盘价'] .min() * 0.95
    fig.update_layout(
        yaxis_range=[min_y,max_y],
        #autosize=False,
        #width=800,
        height=1000,
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    return fig

if __name__ == "__main__":
    app.run_server()
