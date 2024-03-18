import numpy as np
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from pages.chain_overview import chain_page_maps
import components.style as style
from global_service import gs
from dataworks import DataWorks
import akshare as ak
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

dash.register_page(__name__, path="/variety/basis")

variety_page_maps = {}
active_variety_page = None

chart_config = html.Div(
    [
        dbc.Label('选择分析指标：', color='darkblue'),
        dbc.Checklist(
            options=['基差率', '库存', '仓单', '持仓量', '库存消费比', '库存+仓单', '现货利润', '盘面利润', '现货利润+盘面利润'],
            value=['基差率', '库存', '仓单', '持仓量', '现货利润'],
            id='select-index', inline=True
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
            id="radio-future-price", inline=True
        ),

        html.Hr(),
        dbc.Label('标记区间：', color='darkblue'),
        dbc.Checklist(
            options=['现货交易月', '指标共振周期'],
            value=['现货交易月', '指标共振周期'],
            id='switch-marker',
            switch=True, inline=True
        ),
        html.Hr(),
        dbc.Label('共振指标设置：', color='darkblue'),
        dbc.Checklist(                    
            options=['基差率', '库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位', '库存|仓单', '现货利润|盘面利润'],
            value=['基差率', '库存历史时间分位'],
            id='select-synchronize-index', inline=True                    
        ),
        html.Hr(),
        dbc.Label('历史分位回溯时间：', color='darkblue'),
        dcc.Slider(
            0, 130, value=36, step=None,
            marks={
                6: '6个月', 12: '1年', 24: '2年', 36: '3年', 60: '5年', 120: '10年', 130: {'label': 'All', 'style': {'color': 'darkblue'}}
            },
            id='look-forward-months'
        ),
    ]
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

# 基本面分析图表面板
tab_main = html.Div([
    # 主框架
    dbc.Row([
        # 左侧面板
        dbc.Col([
            # 配置面板
            # dbc.Row(dbc.Form(main_chart_config)),
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

class VarietyPage:
    def __init__(self, name, chain) -> None:
        self.variety_name = name
        self.chain_name = chain
        # self.page_maps = {}
        self.chain_config = 'futures_nexus/setting/chains.json'
        self.main_content = None
        self.symbol_chain = chain_page_maps[self.chain_name].symbol_chain
        symbol = self.symbol_chain.get_symbol(name)
        symbol.get_spot_months() 
        dws = DataWorks()
        # symbol.variety_data = gs.dataworks.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data['date'] = pd.to_datetime(symbol.variety_data['date'])
        self.symbol = symbol
        self.look_forward_months = 0
        self.main_figure = {}
        self.future_type = ''
        trade_date = ak.tool_trade_date_hist_sina()['trade_date']
        trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
        dt_all = pd.date_range(start=symbol.symbol_data['date'].iloc[0],end=symbol.symbol_data['date'].iloc[-1])
        dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
        self.trade_breaks = list(set(dt_all) - set(trade_date))

    def create_variety_menu(self):
        menu = dbc.Nav(
            [     
                html.I(className="bi bi-gear me-2", style={'font-size': '1.5rem', 'color': 'cornflowerblue'}, id='config-button'),
                dbc.NavLink("基本面分析", href=f"/variety_basis?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
                dbc.NavLink("周期性分析", href=f"/variety_cycle?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
                dbc.NavLink("跨期分析", href=f"/variety_period?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
                # dbc.NavLink("跨品种分析", href=f"/variety_?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
                dbc.NavLink("交易计划", href=f"/variety_plan?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),                
            ],
            pills=True,
        )     
        return menu   
 
    def create_analyzing_layout(self):
        layout = html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("图表设置"), close_button=True),
                        dbc.ModalBody(chart_config),
                        dbc.ModalFooter(
                            dbc.Button(
                                "确定",
                                id="close-button",
                                className="ms-auto",
                                n_clicks=0,
                            )
                        ),
                    ],
                    id="modal-chart-config",
                    centered=True,
                    size="lg",
                    is_open=False,
                ),          
                tab_main            
            ]
        )
        return layout

    def get_layout(self):
        if self.main_content is None:
            menu = self.create_variety_menu()
            analyzing_layout = self.create_analyzing_layout()
            layout = html.Div(
                [
                    dbc.Row(
                        [
                            # dbc.Col(menu),
                            menu,
                            # dbc.Col(index_selector),
                        ],
                    ),
                    dbc.Row(analyzing_layout),
                ],
                # style=style.CONTENT_STYLE
                style={"left": "12rem", "top": "3.5rem", "margin-left": "12rem", "margin-right": "1rem", "padding": "1rem 1rem",}
            )
            self.main_content = layout
        else:
            layout = self.main_content
        return layout
    
    def create_figure(self, show_index=[], future_type=[], mark_cycle=[], sync_index=[], look_forward_months='all'):
        print("Call create_figure")
        symbol = self.symbol

        if (look_forward_months != self.look_forward_months) | (future_type !=self.future_type):
            symbol.calculate_data_rank(future_type, trace_back_months=look_forward_months)
        self.look_forward_months = look_forward_months
        self.future_type = future_type
        fig_rows = len(show_index) + 1
        specs = [[{"secondary_y": True}] for _ in range(fig_rows)]
        row_widths = [0.1] * (fig_rows - 1) + [0.5]
        subtitles = ['现货/期货价格'] + show_index
        self.main_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.02)
        # 创建主图:期货价格、现货价格、基差
        main_figure = self.main_figure
        fig_future_price = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data[future_type], name='期货价格', 
                                    marker_color='rgb(84,134,240)')
        fig_spot_price = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgba(105,206,159,0.4)')
        fig_basis = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', 
                            marker=dict(color='rgb(239,181,59)', opacity=0.4), showlegend=False) 
        key_mark_sync_index = '指标共振周期'
        if key_mark_sync_index in mark_cycle:
            df_signals =symbol.get_signals(future_type, sync_index)
            signal_nums = len(sync_index)
            df_signals.loc[~((df_signals['信号数量'] == signal_nums) | (df_signals['信号数量'] == -signal_nums)), '信号数量'] = np.nan
            df_signals['位置偏移'] = df_signals['信号数量'].replace([signal_nums, -signal_nums], [0.99, 1.01])
            df_signals['绝对位置'] = df_signals['位置偏移'] * symbol.symbol_data['主力合约收盘价']
            signal_color_mapping ={1.01:'green', 0.99:'red'}
            df_signals['信号颜色'] = df_signals['位置偏移'].map(signal_color_mapping)
            fig_signal = go.Scatter(x=df_signals['date'], y=df_signals['绝对位置'], name='信号', mode='markers', showlegend=False,
                                    marker=dict(size=4, color=df_signals['信号颜色'], colorscale=list(signal_color_mapping.values())))
            main_figure.add_trace(fig_signal, row=1, col=1)        
        main_figure.add_trace(fig_basis, row = 1, col = 1, secondary_y=True) 
        main_figure.add_trace(fig_future_price, row = 1, col = 1)
        main_figure.add_trace(fig_spot_price, row = 1, col = 1)
        
        sub_index_rows = 2
        # 创建副图-基差率,并根据基差率正负配色
        key_basis_rate = '基差率'
        if key_basis_rate in show_index:
            sign_color_mapping = {0:'green', 1:'red'}
            fig_basis_rate = go.Bar(x=symbol.symbol_data['date'], y = symbol.symbol_data['基差率'], name=key_basis_rate,
                                    marker=dict(color=symbol.basis_color['基差率颜色'], colorscale=list(sign_color_mapping.values()),
                                                showscale=False),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_basis_rate, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        histroy_color_mapping ={1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'}
        # 创建副图-库存
        key_storage = '库存'
        symbol.data_rank['库存分位颜色'] = symbol.data_rank['库存历史时间分位'].map(histroy_color_mapping)
        if key_storage in show_index:
            fig_storage = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['库存'], name=key_storage, marker_color='rgb(239,181,59)', showlegend=False,)
            # fig_storage = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['库存'], name='库存', mode='markers', marker=dict(size=2, color='rgb(239,181,59)'))            
            # fig_storage_rank = go.Bar(x=df_rank['date'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color='rgb(234,69,70)')
            fig_storage_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['库存历史时间百分位'], name='库存分位', 
                                    marker=dict(color=symbol.data_rank['库存分位颜色'], opacity=0.6),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_storage_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_storage, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-仓单
        key_receipt = '仓单'
        symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
        if key_receipt in show_index:
            fig_receipt = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['仓单'], name=key_receipt, marker_color='rgb(239,181,59)', showlegend=False,)
            # symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
            # fig_receipt_rank = go.Scatter(x=symbol.data_rank['date'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位', marker_color='rgb(239,181,59)')            
            fig_receipt_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位',
                                        marker=dict(color=symbol.data_rank['仓单分位颜色'], opacity=0.6),
                                        showlegend=False,
                                        hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_receipt_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_receipt, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-持仓量
        key_open_interest = '持仓量'
        open_interest_type = future_type[:4]+'持仓量'
        symbol.data_rank['持仓量分位颜色'] = symbol.data_rank[open_interest_type+'历史时间分位'].map(histroy_color_mapping)
        if key_open_interest in show_index:            
            fig_open_interest = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data[open_interest_type], name=key_receipt, marker_color='rgb(239,181,59)', showlegend=False,)            
            fig_open_interest_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank[open_interest_type+'历史时间百分位'], name='持仓量分位',
                                            marker=dict(color=symbol.data_rank['持仓量分位颜色'], opacity=0.6),
                                            showlegend=False,
                                            hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_open_interest_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_open_interest, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1            

        # 创建副图-现货利润
        key_spot_profit = '现货利润'
        symbol.data_rank['现货利润分位颜色'] = symbol.data_rank['现货利润历史时间分位'].map(histroy_color_mapping)
        if key_spot_profit in show_index:
            # fig_spot_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货利润'], name='现货利润', mode='markers', marker=dict(size=2, color='rgb(234,69,70)'))
            fig_spot_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货利润'], name=key_spot_profit, marker_color='rgb(239,181,59)', showlegend=False,)            
            fig_spot_profit_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['现货利润历史时间百分位'], name='现货利润', 
                                        marker=dict(color=symbol.data_rank['现货利润分位颜色'], opacity=0.6),
                                        showlegend=False,
                                        hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_spot_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_spot_profit, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-盘面利润
        key_future_profit = '盘面利润'
        symbol.data_rank['盘面利润分位颜色'] = symbol.data_rank['盘面利润历史时间分位'].map(histroy_color_mapping)
        if key_future_profit in show_index:
            fig_future_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['盘面利润'], name=key_future_profit, marker_color='rgb(239,181,59)', showlegend=False,)            
            fig_future_profit_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['盘面利润历史时间百分位'], name='盘面利润 ', 
                                            marker=dict(color=symbol.data_rank['盘面利润分位颜色'], opacity=0.6),
                                            showlegend=False,
                                            hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_future_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_future_profit, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 用浅蓝色背景标记现货月时间范围
        key_mark_spot_months = '现货交易月'
        if key_mark_spot_months in mark_cycle:
            main_figure.update_layout(shapes=[])   
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
        # 图表初始加载时,显示最近一年的数据
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
            rangebreaks=[dict(values=self.trade_breaks)],
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
        # 根据 x 轴的范围筛选数据
        filtered_data = symbol.symbol_data[(symbol.symbol_data['date'] >= date_one_year_ago) & (symbol.symbol_data['date'] <= date_now)]
        # 计算 y 轴的最大值和最小值
        max_y = filtered_data[future_type].max()*1.01
        min_y = filtered_data[future_type].min()*0.99
        # max_y2 = filtered_data['基差'].max()*1.01
        # min_y2 = filtered_data['基差'].min()*0.99
        # 设置 y 轴的范围
        main_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
        # main_figure.update_yaxes(range=[min_y2, max_y2], row=1, col=1, secondary_y=True)
        main_figure.update_layout(
            # yaxis_range=[min_y,max_y],
            #autosize=False,
            # width=3000,
            height=800,
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
        print("Return create_figure")
        return main_figure    

    def update_yaxes(self, xaxis_range):
        symbol = self.symbol
        main_figure = self.main_figure
        # xaxis_range = pd.to_datetime(xaxis_range)
        filtered_data = symbol.symbol_data[(symbol.symbol_data['date'] >= xaxis_range[0]) & (symbol.symbol_data['date'] <= xaxis_range[1])]
        # 计算 y 轴的最大值和最小值
        if self.future_type != '':
            max_y = filtered_data[self.future_type].max()*1.01
            min_y = filtered_data[self.future_type].min()*0.99
        # max_y2 = filtered_data['基差'].max()*1.01
        # min_y2 = filtered_data['基差'].min()*0.99        
        main_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
        main_figure.update_xaxes(range=xaxis_range)
        # main_figure.update_yaxes(range=[min_y2, max_y2], row=1, col=1, secondary_y=True)
        return main_figure
    
blank_content = html.Div([
    dbc.Modal(id='modal-chart-config'),
    html.I(id='config-button'),
    dbc.Button(id='close-button'),
    dcc.Graph(id='main-figure-placeholder'),
    dbc.Checklist(id='select-index'),
    dbc.RadioButton(id="radio-future-price"),
    dbc.Checklist(id='switch-marker'),
    dbc.Checklist(id='select-synchronize-index'),
    dcc.Slider(id='look-forward-months')
], style=style.CONTENT_STYLE)

def layout(variety_id=None, chain_id=None, **other_unknown_query_strings):
    if variety_id is None:
        return html.Div([
            dbc.Row(blank_content)
        ])
    chain_page = chain_page_maps[chain_id]
    sidebar = chain_page.sidebar
    if variety_id not in variety_page_maps:
        variety_page = VarietyPage(variety_id, chain_id)
        variety_page_maps[variety_id] = variety_page
    else:
        variety_page = variety_page_maps[variety_id]
    variety_page_maps['active_variety'] = variety_page
    # main_content = html.Div('This is our Home page content.', style=style.CONTENT_STYLE)
    layout = html.Div([
        sidebar, 
        variety_page.get_layout(),
        # main_content,
    ])
    # print("Layout: ", layout)
    return layout

# TODO:
# - 使用 prevent_initial_call避免以input的初始值调用回调函数
# - 使用PreventUpdate和dash.no_update明确不需要更新的内容
# - 使用callback_context和Patch针对性处理变化的input并进行部分更新
# - 使用memoization机制处理无参数变化的输入
# - 使用Store存储/传递共享数据
# Add controls to build the interaction
@callback(
    Output('main-figure-placeholder', 'figure'),
    Input('select-index', 'value'),
    Input('radio-future-price', 'value'),
    Input('switch-marker', 'value'),
    Input('select-synchronize-index', 'value'),
    Input('look-forward-months', 'value'),
    # allow_duplicate=True
)
def update_graph(select_index_value, radio_future_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value):   
    if 'active_variety' not in variety_page_maps:
        return dash.no_update
    # print(f'on_update_graph: {variety_page_maps['active_variety'].variety_name}')
    variety_page = variety_page_maps['active_variety']
    symbol = variety_page.symbol
    # if symbol.name not in page_property['chart_setting']:
    #     page_property['chart_setting'][symbol.name] = {}
        # initial_data()
        # page_property['symbol_figure'] = commodity.SymbolFigure(symbol)
    symbol_chain = variety_page.symbol_chain
    df_profit = symbol.get_profits(radio_future_value, symbol_chain)    
    figure = variety_page.create_figure(select_index_value, radio_future_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value)
    return figure

@callback(
    Output("modal-chart-config", "is_open"),
    [Input("config-button", "n_clicks"), Input("close-button", "n_clicks")],
    [State("modal-chart-config", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open