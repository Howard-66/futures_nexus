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

# 创建主品种数据
symbol_id = 'RB'
symbol_name = '螺纹钢'
fBasePath = 'steel/data/mid-stream/螺纹钢/'
json_file = './steel/setting.json'
symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

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
                    options=['基差率', '库存', '库存-历史分位', '仓单', '仓单-历史分位', '库存消费比', '现货利润', '现货利润-历史分位', '盘面利润', '盘面利润-历史分位'],
                    value=['基差率', '库存-历史分位', '仓单-历史分位', '现货利润-历史分位', '盘面利润-历史分位'],
                    id='select_synchronize_index',
                    inline=True                    
                ),
                dbc.Label('或关系指标设置：', color='darkblue'),
                dbc.Checklist(
                    options=['库存|仓单', '现货利润|盘面利润'],
                    value=['库存|仓单', '现货利润|盘面利润'],
                    id='switch_or_index',
                    switch=True,
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
            dbc.Row(main_chart_config),
            # 图表面板
            dbc.Row(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(figure={}, id='graph-placeholder'),    
                    ])
                )
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
                                dbc.Placeholder(size="lg", className="me-1 mt-1 w-100"),
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
                        dbc.Tab(tab2_content, label="Tab 2", tab_id="tab-2"),
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

def initial_data():
    merged_data = symbol.merge_data()
    # 生成上由原材料的现货和期货价格数据
    symbol_j = commodity.SymbolData('J', '焦炭', json_file)
    symbol_j.merge_data()
    symbol_i = commodity.SymbolData('I', '铁矿石', json_file)
    symbol_i.merge_data()
    profit_j = symbol_j.symbol_data[['日期', '现货价格', '主力合约结算价']].copy()
    profit_j.rename(columns={'现货价格': symbol_j.name+'现货', '主力合约结算价': symbol_j.name+'期货'}, inplace=True)
    profit_i = symbol_i.symbol_data[['日期', '现货价格', '主力合约结算价']].copy()
    profit_i.rename(columns={'现货价格': symbol_i.name+'现货', '主力合约结算价': symbol_i.name+'期货'}, inplace=True)
    # 计算品种的现货利润和盘面利润
    formula = symbol.symbol_setting['ProfitFormula']
    df_profit = pd.merge(profit_j, profit_i, on='日期', how='outer')
    df_profit = pd.merge(symbol.symbol_data[['日期', '现货价格', '主力合约结算价']], df_profit, on='日期', how='outer').dropna(axis=0, how='all', subset=['现货价格', '主力合约结算价'])
    df_profit['现货利润'] = df_profit['现货价格'] - formula[symbol_j.name] * df_profit[symbol_j.name+'现货'] - formula[symbol_j.name] * df_profit[symbol_i.name+'现货'] - formula['其他成本']
    df_profit['盘面利润'] = df_profit['主力合约结算价'] - formula[symbol_j.name] * df_profit[symbol_j.name+'期货'] - formula[symbol_i.name] * df_profit[symbol_i.name+'期货'] - formula['其他成本']
    df_profit.dropna(axis=0, how='all', subset=['现货利润', '盘面利润'], inplace=True)
    df_append = df_profit[['日期', '现货利润', '盘面利润']].copy()
    symbol.symbol_data = pd.merge(symbol.symbol_data, df_append, on='日期', how='outer')
    # 计算各指标的历史百分位和历史分位数据
    symbol.calculate_data_rank(trace_back_months=60)

main_figure = make_subplots(rows=6, cols=1, shared_xaxes=True, 
                            specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]],
                            vertical_spacing=0.01, 
                            subplot_titles=('基差分析', '基差率', '库存', '仓单', '现货利润', '盘面利润'), 
                            row_width=[0.1, 0.1, 0.1, 0.1, 0.1, 0.7])

def create_main_chart():
    # 创建主图：期货价格、现货价格、基差
    fig_future_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['主力合约收盘价'], name='期货价格', 
                                marker_color='rgb(84,134,240)')
    fig_spot_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgb(105,206,159)')
    fig_basis = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', 
                        marker=dict(color='rgb(239,181,59)', opacity=0.4), showlegend=False)
    main_figure.add_trace(fig_basis, secondary_y=True)
    main_figure.add_trace(fig_future_price, row = 1, col = 1)
    main_figure.add_trace(fig_spot_price, row = 1, col = 1)

# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='select_index', component_property='value')
)
def update_graph(col_chosen):
    initial_data()
    symbol.get_spot_months()
    create_main_chart()

    # 创建副图-基差率，并根据基差率正负配色
    sign_color_mapping = {0:'green', 1:'red'}
    fig_basis_rate = go.Bar(x=symbol.symbol_data['日期'], y = symbol.symbol_data['基差率'], name='基差率',
                            marker=dict(color=symbol.basis_color['基差率颜色'], colorscale=list(sign_color_mapping.values()),
                                        showscale=False),
                            showlegend=False,
                            hovertemplate='%{y:.2%}')
    main_figure.add_trace(fig_basis_rate, row = 2, col = 1)

    histroy_color_mapping ={1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'}

    # 创建副图-库存
    fig_storage = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name='库存', marker_color='rgb(239,181,59)')
    # fig_storage = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name='库存', mode='markers', marker=dict(size=2, color='rgb(239,181,59)'))
    symbol.data_rank['库存分位颜色'] = symbol.data_rank['库存历史时间分位'].map(histroy_color_mapping)
    # fig_storage_rank = go.Bar(x=df_rank['日期'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color='rgb(234,69,70)')
    fig_storage_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['库存历史时间百分位'], name='库存分位', 
                              marker=dict(color=symbol.data_rank['库存分位颜色'], opacity=0.6),
                              showlegend=False,
                              hovertemplate='%{y:.2%}')
    main_figure.add_trace(fig_storage_rank, row = 3, col = 1, secondary_y=True)
    main_figure.add_trace(fig_storage, row = 3, col = 1)

    # 创建副图-仓单
    fig_receipt = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['仓单'], name='仓单', marker_color='rgb(239,181,59)')
    # symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
    # fig_receipt_rank = go.Scatter(x=symbol.data_rank['日期'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位', marker_color='rgb(239,181,59)')
    symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
    fig_receipt_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位',
                                marker=dict(color=symbol.data_rank['仓单分位颜色'], opacity=0.6),
                                showlegend=False,
                                hovertemplate='%{y:.2%}')
    main_figure.add_trace(fig_receipt_rank, row = 4, col = 1, secondary_y=True)
    main_figure.add_trace(fig_receipt, row = 4, col = 1)

    # 创建副图-现货利润
    # fig_spot_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货利润'], name='现货利润', mode='markers', marker=dict(size=2, color='rgb(234,69,70)'))
    fig_spot_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货利润'], name='现货利润', marker_color='rgb(239,181,59)')
    symbol.data_rank['现货利润分位颜色'] = symbol.data_rank['现货利润历史时间分位'].map(histroy_color_mapping)
    fig_spot_profit_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['现货利润历史时间百分位'], name='现货利润', 
                                  marker=dict(color=symbol.data_rank['现货利润分位颜色'], opacity=0.6),
                                  showlegend=False,
                                  hovertemplate='%{y:.2%}')
    main_figure.add_trace(fig_spot_profit_rank, row = 5, col = 1, secondary_y=True)
    main_figure.add_trace(fig_spot_profit, row = 5, col = 1)

    # 创建副图-盘面利润
    fig_future_profit = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['盘面利润'], name='盘面利润', marker_color='rgb(239,181,59)')
    symbol.data_rank['盘面利润分位颜色'] = symbol.data_rank['盘面利润历史时间分位'].map(histroy_color_mapping)
    fig_future_profit_rank = go.Bar(x=symbol.data_rank['日期'], y=symbol.data_rank['盘面利润历史时间百分位'], name='盘面利润 ', 
                                    marker=dict(color=symbol.data_rank['盘面利润分位颜色'], opacity=0.6),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
    main_figure.add_trace(fig_future_profit_rank, row = 6, col = 1, secondary_y=True)
    main_figure.add_trace(fig_future_profit, row = 6, col = 1)

    # 根据交易时间过滤空数据
    trade_date = ak.tool_trade_date_hist_sina()['trade_date']
    trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
    dt_all = pd.date_range(start=symbol.symbol_data['日期'].iloc[0],end=symbol.symbol_data['日期'].iloc[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(trade_date))

    for _, row in symbol.spot_months.iterrows():
        main_figure.add_shape(
            # 矩形
            type="rect",
            # 矩形的坐标
            x0=row['Start Date'],
            x1=row['End Date'],
            y0=0,
            y1=1,
            xref='x',
            yref='paper',
            # 矩形的颜色和透明度
            fillcolor="LightBlue",
            opacity=0.1,
            # 矩形的边框
            line_width=0,
            # 矩形在数据之下
            layer="below"
        )

    # X轴坐标按照年-月显示
    main_figure.update_xaxes(
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
    main_figure.update_layout(
        yaxis_range=[min_y,max_y],
        #autosize=False,
        #width=800,
        height=1200,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='WhiteSmoke',
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        yaxis2_showgrid=False,        
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
    return main_figure

if __name__ == "__main__":
    app.run_server()
