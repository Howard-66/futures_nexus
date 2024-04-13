import numpy as np
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State
# import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
# from pages.chain_overview import chain_page_maps
# import components.style as style
from global_service import gs
from dataworks import DataWorks
import akshare as ak
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from variety import SymbolData

dash.register_page(__name__, path="/variety/basis")

variety_page_maps = {}
active_variety_page = None

chart_config = html.Div(
    [
        dmc.CheckboxGroup(
            label='选择分析指标：',
            children=[
                dmc.Checkbox(label='基差率', value='基差率'),
                dmc.Checkbox(label='库存', value='库存'),
                dmc.Checkbox(label='仓单', value='仓单'),
                dmc.Checkbox(label='持仓量', value='持仓量'),
                dmc.Checkbox(label='库存消费比', value='库存消费比'),
                dmc.Checkbox(label='库存+仓单', value='库存+仓单'),
                dmc.Checkbox(label='现货利润', value='现货利润'),
                dmc.Checkbox(label='盘面利润', value='盘面利润'),
                dmc.Checkbox(label='现货利润+盘面利润', value='现货利润+盘面利润'),
            ],
            value=['基差率', '库存', '仓单', '持仓量', '现货利润'],
            id='select-index',
        ),
        html.Hr(),
        dmc.RadioGroup(
            label='选择期货价格类型：',
            children=[
                dmc.Radio(label='主力合约收盘价', value='主力合约收盘价'),
                dmc.Radio(label='主力合约结算价', value='主力合约结算价'),
                dmc.Radio(label='近月合约收盘价', value='近月合约收盘价'),
                dmc.Radio(label='近月合约结算价', value='近月合约结算价'),                
            ],
            value='主力合约收盘价',
            id='radio-future-price',
        ),
        html.Hr(),
        dmc.CheckboxGroup(
            label='标记区间：',
            children=[
                dmc.Checkbox(label='现货交易月', value='现货交易月'),
                dmc.Checkbox(label='指标共振周期', value='指标共振周期'),
            ],
            value=['现货交易月', '指标共振周期'],
            id='switch-marker',
        ),
        html.Hr(),
        dmc.CheckboxGroup(
            label='共振指标设置：',
            children=[
                dmc.Checkbox(label='基差率', value='基差率'),
                dmc.Checkbox(label='库存历史时间分位', value='库存历史时间分位'),
                dmc.Checkbox(label='仓单历史时间分位', value='仓单历史时间分位'),
                dmc.Checkbox(label='现货利润历史时间分位', value='现货利润历史时间分位'),
                dmc.Checkbox(label='盘面利润历史时间分位', value='盘面利润历史时间分位'),
                dmc.Checkbox(label='库存|仓单', value='库存|仓单'),
                dmc.Checkbox(label='现货利润|盘面利润', value='现货利润|盘面利润'),
            ],
            value=['基差率', '库存历史时间分位'],
            id='select-synchronize-index',
        ),
        html.Hr(),
        dmc.Text('历史分位回溯时间：', color='darkblue'),
        dmc.Slider(
            value=36, min=6, max=130, step=None,
            marks={
                6: '6个月', 12: '1年', 24: '2年', 36: '3年', 60: '5年', 120: '10年', 130: {'label': 'All', 'style': {'color': 'darkblue'}}
            },
            id='look-forward-months'
        ),
    ]
)

analyzing_log = html.Div([
    dmc.Text('量化分析标签', color='darkblue'),
    html.Div(
        html.Span(
            id='html-analyzing-tags'
        ),    
    ),
    html.Hr(),
    dmc.Text('盈利-风险测算', color='darkblue'),
    # dbc.RadioItems(
    #     options=[
    #         {"label": "单边/跨期做多", "value": '单边/跨期做多'},
    #         {"label": "单边/跨期做空", "value": '单边/跨期做空'},
    #     ],
    #     value='单边/跨期做多',
    #     id="radio_trade_type", inline=True
    # ),       
    html.Div(id='html-profit-loss'),
    html.Hr(),
    dmc.Text('综合分析', color='darkblue'),
    dmc.Textarea(placeholder="分析结论", id='txt-log-conclusion'),
    html.Div([
        dmc.Button("删除", color="red", id='bt-log-delete'),
        dmc.Button("保存", color="blue", id='bt-log-save'),
    ])
])

# 基本面分析图表面板
tab_main = html.Div([
    # 主框架
    dmc.Grid([
        # 左侧面板
        dmc.Col(
            # 图表面板
            [
                # dmc.Space(h=40),
                dcc.Graph(figure={}, id='main-figure-placeholder'),      
            ],                            
            span=9),
        # 右侧面板
        dmc.Col([            
            dmc.Stack(
                [
                    # 期限结构分析图表
                    dmc.Paper(
                        dcc.Graph(figure={}, id='term-figure-placeholder'),
                        shadow="sm",
                        radius="xs",
                        p="xs",
                        withBorder=True,                           
                    ),
                    # 跨期分析图表
                    dmc.Paper(
                        dcc.Graph(figure={}, id='intertemporal-figure-placeholder'),
                        shadow="sm",
                        radius="xs",
                        p="xs",
                        withBorder=True,                           
                    ),         
                    dmc.Paper(
                        analyzing_log,
                        shadow="sm",
                        radius="xs",
                        p="xs",
                        withBorder=True,                           
                    ),     
                ],  
                p=10,
            ),
        ], span=3)
    ])
])

class VarietyPage:
    def __init__(self, name) -> None:
        self.variety_name = name
        # self.chain_name = chain
        # self.page_maps = {}
        # self.chain_config = 'futures_nexus/setting/chains.json'
        self.main_content = None
        # self.symbol_chain = chain_page_maps[self.chain_name].symbol_chain
        # symbol = self.symbol_chain.get_symbol(name)
        symbol = SymbolData(name)
        symbol_data = symbol.merge_data()
        symbol.get_spot_months() 
        dws = DataWorks()
        # symbol.variety_data = gs.dataworks.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data['date'] = pd.to_datetime(symbol.variety_data['date'])
        self.symbol = symbol
        self.look_forward_months = 0
        self.main_figure = None
        self.on_layout = False
        self.future_type = ''
        trade_date = dws.get_trade_date()
        trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
        dt_all = pd.date_range(start=symbol.symbol_data['date'].iloc[0],end=symbol.symbol_data['date'].iloc[-1])
        dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
        self.trade_breaks = list(set(dt_all) - set(trade_date))        

    def create_variety_menu(self):
        # menu = dbc.Nav(
        #     [     
        #         html.I(className="bi bi-gear me-2", style={'font-size': '1.5rem', 'color': 'cornflowerblue'}, id='config-button'),
        #         dbc.NavLink("基本面分析", href=f"/variety_basis?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
        #         dbc.NavLink("周期性分析", href=f"/variety_cycle?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
        #         dbc.NavLink("跨期分析", href=f"/variety_period?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
        #         # dbc.NavLink("跨品种分析", href=f"/variety_?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
        #         dbc.NavLink("交易计划", href=f"/variety_plan?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),                
        #     ],
        #     pills=True,
        # )     
        return None   
 
    def create_analyzing_layout(self):
        layout = html.Div(
            [
                dmc.Modal(
                    title="图表设置",
                    id="modal-chart-config",
                    size="xl",
                    centered=True,
                    opened=False,
                    children=[
                        chart_config,
                        dmc.Space(h=20),
                        dmc.Group(
                            [
                                dmc.Button("确定", id="close-button"),
                            ],
                        )
                    ],            
                ),                
                tab_main,
            ],
        )
        return layout

    def get_layout(self):
        if self.main_content is None:
            menu = self.create_variety_menu()
            analyzing_layout = self.create_analyzing_layout()
            layout = html.Div(
                [
                    analyzing_layout,
                ],
            )
            self.main_content = layout
        else:
            layout = self.main_content
        self.on_layout = True
        return layout
    
    def create_figure(self, show_index=[], future_type=[], mark_cycle=[], sync_index=[], look_forward_months='all'):
        symbol = self.symbol
        if (look_forward_months != self.look_forward_months) | (future_type !=self.future_type):
            symbol.calculate_data_rank(future_type, trace_back_months=look_forward_months)
        self.look_forward_months = look_forward_months
        self.future_type = future_type
        fig_rows = len(show_index) + 1
        specs = [[{"secondary_y": True}] for _ in range(fig_rows)]
        row_widths = [0.1] * (fig_rows - 1) + [0.5]
        subtitles = ['现货/期货价格'] + show_index
        main_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.02)
        # 创建主图:期货价格、现货价格、基差
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
        if key_storage in symbol.symbol_data.columns:
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
        if key_receipt in symbol.symbol_data.columns:
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
        if key_spot_profit in symbol.symbol_data.columns:
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
        if key_future_profit in symbol.symbol_data.columns:        
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
            # rangeselector = dict(
            #     buttons = list([
            #         dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            #         dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            #         # dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),                
            #         dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
            #         dict(step = 'all')
            #         ]))
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
            autosize=True,
            # width=3000,
            height=1200,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='WhiteSmoke',  
            hovermode='x unified',
            modebar={},
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
        self.main_figure = main_figure
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

    def display_term_structure_figure(self, click_date, spot_price):
        symbol = self.symbol
        df_term = symbol.variety_data 
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

    def display_cross_term_figure(self, click_date, domain_contract):
        symbol = self.symbol
        half_year_later = click_date + timedelta(days=180)
        date_now = datetime.now()
        end_date = half_year_later if date_now>half_year_later else date_now
        start_date = click_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')    
        df_term = symbol.variety_data   
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
                                    rangebreaks=[dict(values=self.trade_breaks)],
                                    range=[start_date, end_date],)
        cross_term_figure.update_yaxes(showgrid=False)
        cross_term_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
        return cross_term_figure, profit_loss

blank_content = html.Div([
    html.Div(id='methods-navlink'),
    dmc.SegmentedControl(id='segmented-variety-switcher', data=[]),
    dmc.Select(id='variety-select'),
    dmc.Modal(id='modal-chart-config'),
    html.I(id='config-button'),
    dmc.Button(id='close-button'),
    dcc.Graph(id='main-figure-placeholder'),
    dmc.CheckboxGroup(id='select-index'),
    dmc.RadioGroup(id="radio-future-price"),
    dmc.CheckboxGroup(id='switch-marker'),
    dmc.CheckboxGroup(id='select-synchronize-index'),
    dmc.Slider(id='look-forward-months'),
    html.Span(id='html-analyzing-tags'),
    html.Div(id='html-profit-loss'),
    dmc.Textarea(id='txt-log-conclusion'),
    dmc.Button(id='bt-log-delete'),
    dmc.Button(id='bt-log-save'),
    dcc.Graph(id='term-figure-placeholder'),
    dcc.Graph(id='intertemporal-figure-placeholder')
])

def layout(variety_id=None, **other_unknown_query_strings):
    if variety_id is None:
        return html.Div([
            blank_content
        ])
    # chain_page = chain_page_maps[chain_id]
    # sidebar = chain_page.sidebar
    if variety_id not in variety_page_maps:
        variety_page = VarietyPage(variety_id)
        variety_page_maps[variety_id] = variety_page
    else:
        variety_page = variety_page_maps[variety_id]
    variety_page_maps['active_variety'] = variety_page

    layout = html.Div([
        # sidebar, 
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
    variety_page = variety_page_maps['active_variety']
    if variety_page.on_layout and variety_page.main_figure is not None:
        figure = variety_page.main_figure
        variety_page.on_layout = False
    else:
        symbol = variety_page.symbol
        # symbol_chain = variety_page.symbol_chain
        # df_profit = symbol.get_profits(radio_future_value, symbol_chain)    
        figure = variety_page.create_figure(select_index_value, radio_future_value, switch_marker_value, select_synchronize_index_value, look_forward_months_value)
    return figure

@callback(
    Output("modal-chart-config", "opened"),
    [Input("button-methond-config", "n_clicks"), Input("close-button", "n_clicks")],
    [State("modal-chart-config", "opened")],
)
def toggle_modal(n1, n2, opened):
    if n1 or n2:
        return not opened
    return opened

    
@callback(
    Output('term-figure-placeholder', 'figure'),
    Output('intertemporal-figure-placeholder', 'figure'),
    # Output('radio_trade_type', 'value'),
    Output('html-analyzing-tags', 'children'),
    Output('html-profit-loss', 'children'),
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
        variety_page = variety_page_maps['active_variety']
        symbol = variety_page.symbol
        # 获取第一个被点击的点的信息
        point_data = clickData['points'][0]
        # 获取x轴坐标
        display_date = point_data['x']
        click_date = datetime.strptime(display_date, '%Y-%m-%d')
        spot_price = point_data['y']
        # 绘制期限结构视图
        term_fig, df_dominant_contract, term_flag = variety_page.display_term_structure_figure(click_date, spot_price)
        # 绘制跨期套利分析视图
        cross_term_figure, profit_loss = variety_page.display_cross_term_figure(click_date, df_dominant_contract)
        # print(profit_loss)
        # 准备分析日志数据
        flag_color ={'Long': 'red', 'Short': 'lime', 'X': 'gray'}
        flag_color2 ={'red': 'red', 'green': 'lime', 'gray': 'gray'}        
        trade_type = {'Long': '单边/跨期做多', 'Short': '单边/跨期做空'}
        basis = clickData['points'][2]['y']
        basis_flag = 'Long' if basis>0 else 'Short'
        click_data = symbol.data_rank[symbol.data_rank['date']==click_date]
        inventory_flag = click_data['库存分位颜色'].iloc[0]
        receipt_flag = click_data['仓单分位颜色'].iloc[0]
        openinterest_flag = click_data['持仓量分位颜色'].iloc[0]

        html_analyzing_tags =[
            #     dbc.Badge("远月/近月/交割月", color="primary", className="me-1",id='log_period'),
            #     html.Span(" | "),
                dmc.Badge("基差", color=flag_color[basis_flag], id='log_basis'),
                dmc.Badge("期限结构", color=flag_color[term_flag], id='log_term_structure'),
                html.Span(" | "),
                dmc.Badge("库存", color=flag_color2[inventory_flag], id='log_inventory'),
                dmc.Badge("仓单", color=flag_color2[receipt_flag], id='log_receipt'),
                dmc.Badge("持仓量", color=flag_color2[openinterest_flag], id='log_open_interest'),
                html.Span(" | "),                                
        ]
        if '现货利润' in symbol.symbol_data.columns:       
            spotprofit_flag = click_data['现货利润分位颜色'].iloc[0]
            html_analyzing_tags.append(dmc.Badge("现货利润", color=flag_color2[spotprofit_flag], id='log_spot_profit'))
        if '盘面利润' in symbol.symbol_data.columns:    
            futureprofit_flag = click_data['盘面利润分位颜色'].iloc[0]
            html_analyzing_tags.append(dmc.Badge("盘面利润", color=flag_color2[futureprofit_flag],  id='log_future_profit'),)
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
        columns, values = df.columns, df.values
        header = [html.Tr([html.Th(col) for col in columns])]
        rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]      
        html_profit_loss = dmc.Table([html.Thead(header), html.Tbody(rows)], striped=True, highlightOnHover=True, withBorder=False, withColumnBorders=False)
        return term_fig, cross_term_figure, html_analyzing_tags, html_profit_loss
        # return term_fig, cross_term_figure, trade_type[basis_flag], flag_color[basis_flag], flag_color[term_flag], flag_color2[inventory_flag], flag_color2[receipt_flag], flag_color2[openinterest_flag], flag_color2[spotprofit_flag], flag_color2[futureprofit_flag], 
    else:
        return {}, {}, {}, {}
        # return {}, {}, '', 'dark', 'dark', 'dark', 'dark', 'dark', 'dark', 'dark'

@callback(
    Output(component_id='main-figure-placeholder', component_property='figure', allow_duplicate=True),
    Input('main-figure-placeholder', 'relayoutData'),
    prevent_initial_call=True
)
def display_relayout_data(relayoutData):
    # if 'symbol_figure' not in page_property:
    #     return dash.no_update
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        variety_page = variety_page_maps['active_variety']
        xaxis_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
        main_figure = variety_page.update_yaxes(xaxis_range)
        return main_figure
    else:
        return dash.no_update