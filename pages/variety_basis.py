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
import plotly.express as px
from plotly.subplots import make_subplots
from variety import SymbolData

dash.register_page(__name__, path="/variety/basis")

variety_page_maps = {}
active_variety_page = None

quant_tags = html.Div([
    dmc.Text('量化分析标签', c='darkblue'),
    html.Div(
        html.Span(
            id='html-analyzing-tags'
        ),    
    ),
])

analyzing_log = html.Div([
    dmc.Text('盈利-风险测算', c='darkblue'),
    html.Div(id='html-profit-loss'),
    # html.Hr(),
    # dmc.Text('综合分析', color='darkblue'),
    # dmc.Textarea(placeholder="分析结论", id='txt-log-conclusion'),
    # html.Div([
    #     dmc.Button("删除", color="red", id='bt-log-delete'),
    #     dmc.Button("保存", color="blue", id='bt-log-save'),
    # ])
])

right_panel = dmc.Stack(
    [
        # 量化标签
        dmc.Paper(
            quant_tags,
            shadow="sm",
            radius="xs",
            p="xs",
            withBorder=True,                           
        ),          
        # 期限结构分析图表
        dmc.Paper(
            dcc.Graph(figure={}, id='term-figure-placeholder', config={'displayModeBar': False}),
            shadow="sm",
            radius="xs",
            p="xs",
            withBorder=True,                           
        ),
        # 跨期分析图表
        dmc.Paper(
            dcc.Graph(figure={}, id='intertemporal-figure-placeholder', config={'displayModeBar': False}),
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
)

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
        self.show_indexs = None
        self.future_type = ''
        # 获取用户设置
        self.user_json='setting/user.json'
        user_setting = dws.load_json_setting(self.user_json)
        if symbol.id not in user_setting:
            user_setting[symbol.id] = {}
            # dws.save_json_setting(self.user_json, user_setting)        
        self.user_setting = user_setting
        # 生成非交易日列表
        trade_date = dws.get_trade_date()
        trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
        dt_all = pd.date_range(start=symbol.symbol_data['date'].iloc[0],end=symbol.symbol_data['date'].iloc[-1])
        dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
        self.trade_breaks = list(set(dt_all) - set(trade_date))        
        dws.close()
 
    def create_analyzing_layout(self):
        all_fields = self.symbol.get_data_fields()
        if 'ShowIndexs' in self.user_setting[self.symbol.id]:
            show_fields = self.user_setting[self.symbol.id]['ShowIndexs']
        else:
            show_fields = all_fields           
        left_panel = dmc.Stack(
            [
                # 图表配置面板
                dmc.Space(h=2),
                dmc.Group(
                    [
                        dmc.Text("分析指标:", size='xs'),
                        dmc.ChipGroup(
                            [dmc.Chip(x, value=x, variant="outline", radius="md", size="xs") for x in all_fields],
                            id="show-indexs",
                            value=show_fields, # TODO: Load from config file
                            multiple=True,
                        ),
                        dmc.Divider(orientation='vertical'),
                        dmc.Text("价格类型:", size='xs'),
                        dmc.Select(
                            size='xs',
                            data=[
                                {'label': '主力合约', 'value': '主力合约'},
                                {'label': '近月合约', 'value': '近月合约'}],
                            value='主力合约',
                            id='price-type',
                            style={'width': 100}
                        ),
                        dmc.Divider(orientation='vertical'),
                        dmc.Switch(label="现货交易月", id="mark-spot-months", checked=True, radius="lg", size='xs'),                        
                        dmc.Divider(orientation='vertical'),
                        dmc.Text("回溯周期:", size='xs'),
                        dmc.Select(
                            size='xs',
                            data=[
                                {'label': '6个月', 'value': 6},
                                {'label': '1年', 'value': 12},
                                {'label': '2年', 'value': 24},
                                {'label': '3年', 'value': 36},
                                {'label':'5年', 'value': 60},
                                {'label':'全部', 'value': 0}],
                            value=12,
                            id='trace-back-months',
                            style={'width': 80}
                        ),
                    ],
                ),
                # 图表面板
                dmc.LoadingOverlay(dcc.Graph(id='main-figure-placeholder', config={'displayModeBar': False}),)
            ],
            spacing=5,
        )              
        layout = dmc.Grid([
                    # 左侧面板
                    dmc.Col(left_panel, span=9),
                    # 右侧面板
                    dmc.Col(right_panel, span=3)
        ])        
        return layout

    def get_layout(self):
        if self.main_content is None:
            analyzing_layout = self.create_analyzing_layout()
            layout = html.Div(
                [
                    analyzing_layout,
                ],
            )
            self.main_content = layout
        else:
            # print(self.main_content.children[0].children[0].children)
            # print(self.main_content.children[0].children[0].children.children[1].children[1])
            self.main_content.children[0].children[0].children.children[1].children[1].value=self.show_indexs
            layout = self.main_content
        self.on_layout = True
        return layout
    
    def create_figure(self, show_index, future_type, mark_spot_months, sync_index, look_forward_months):        
        symbol = self.symbol
        # show_index = symbol.get_data_fields()
        if show_index != self.show_indexs:
            self.user_setting[symbol.id]['ShowIndexs'] = show_index
            dws = DataWorks()
            dws.save_json_setting(self.user_json, self.user_setting)    
            dws.close()
            self.show_indexs = show_index
        # for i, item in enumerate(show_index):
        #     if item == '持仓量':
        #         show_index[i] = future_type+'持仓量'        
        #         break
        future_type = future_type+'结算价'
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
                            marker=dict(color='rgb(239,181,59)', opacity=0.6), showlegend=False) 
        # 绘制信号
        mark_signals = True
        if mark_signals:
            df_signals =symbol.get_signals(sync_index)
            signal_nums = len(sync_index)
            df_signals.loc[~((df_signals['信号数量'] == signal_nums) | (df_signals['信号数量'] == -signal_nums)), '信号数量'] = np.nan
            df_signals['位置偏移'] = df_signals['信号数量'].replace([signal_nums, -signal_nums], [0.99, 1.01])
            df_signals['绝对位置'] = df_signals['位置偏移'] * symbol.symbol_data['主力合约收盘价']
            signal_color_mapping ={1.01:'green', 0.99:'red'}
            df_signals['信号颜色'] = df_signals['位置偏移'].map(signal_color_mapping)
            fig_signal = go.Scatter(x=df_signals['date'], y=df_signals['绝对位置'], name='信号', mode='markers', showlegend=False,
                                    marker=dict(size=4, color=df_signals['信号颜色'], colorscale=list(signal_color_mapping.values())))
            main_figure.add_trace(fig_signal, row=1, col=1)        
        main_figure.update_xaxes(linecolor='gray', tickfont=dict(color='gray'), row=1, col=1)
        main_figure.update_yaxes(linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1, row=1, col=1)
        main_figure.add_trace(fig_basis, row = 1, col = 1, secondary_y=True) 
        main_figure.add_trace(fig_future_price, row = 1, col = 1)
        main_figure.add_trace(fig_spot_price, row = 1, col = 1)

        histroy_color_mapping ={1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'}        
        index_color_mapping = {
            'AmountN': {1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'},
            'AmountP': {1:'green', 2:'gray', 3:'gray', 4:'gray', 5:'red'},
            'RateN': {1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'},
            'RateP': {1:'green', 2:'gray', 3:'gray', 4:'gray', 5:'red'},
            'NP1N': {-1: 'red', -0.5:'gray', 0:'gray', 0.5:'gray', 1:'green'},
            'NP1P': {-1: 'green', -0.5:'gray', 0:'gray', 0.5:'gray', 1:'red'},
        }
        sub_index_rows = 2
        data_index = symbol.symbol_setting['DataIndex']
        for index in show_index:
            typed_index = f"{future_type[:4]}持仓量" if index=='持仓量' else index
            dateindex_type = data_index[typed_index]['Type']        
            if dateindex_type=='NP1P' or dateindex_type=='NP1N':
                symbol.data_rank[index+'颜色'] = symbol.data_rank[index].map(index_color_mapping[dateindex_type])
            else:
                symbol.data_rank[index+'颜色'] = symbol.data_rank[index+'分位'].map(index_color_mapping[dateindex_type])
            # fig_storage = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['库存'], name=key_storage, marker_color='rgb(239,181,59)', showlegend=False,)
            fig_index = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank[index], name=index, 
                                marker=dict(color=symbol.data_rank[index+'颜色'], opacity=0.6),
                                showlegend=False,
                                # hovertemplate='%{y:.2%}',
                                )
            # main_figure.add_trace(fig_storage_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.update_xaxes(linecolor='gray', tickfont=dict(color='gray'), row=sub_index_rows, col=1)
            main_figure.update_yaxes(linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1, row=sub_index_rows, col=1)
            
            main_figure.add_trace(fig_index, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 用浅蓝色背景标记现货月时间范围
        if mark_spot_months:
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
        max_y2 = filtered_data['基差率'].max()*1.01
        min_y2 = filtered_data['基差率'].min()*0.99        
        max_y3 = filtered_data['基差'].max()*1.01
        min_y3 = filtered_data['基差'].min()*0.99    
        # 设置 y 轴的范围
        main_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
        main_figure.update_yaxes(range=[min_y2, max_y2], row=2, col=1, secondary_y=False)
        main_figure.update_yaxes(range=[min_y3, max_y3], row=1, col=1, secondary_y=True)
        main_figure.update_layout(
            # yaxis_range=[min_y,max_y],
            autosize=True,
            # width=3000,
            height=1200,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='#f5f5f5',  
            paper_bgcolor='#f5f5f5',
            hovermode='x unified',
            modebar={},
            legend=dict(
                orientation='h',
                yanchor='top',
                y=1,
                xanchor='left',
                x=0,
                # bgcolor='#f5f5f5',
                # bordercolor='LightSteelBlue',
                # borderwidth=0
            ),
        )
        main_figure.update_annotations(dict(
            x=0,  # x=0 表示最左边
            xanchor='left',  # 锚点设置为左边
            xref="paper",  # 位置参考整个画布的宽度
            yref="paper",  # 位置参考整个画布的高度
            font=dict(size=12)  # 可选的字体大小设置
        ))        
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
        max_y2 = filtered_data['基差率'].max()*1.01
        min_y2 = filtered_data['基差率'].min()*0.99        
        max_y3 = filtered_data['基差'].max()*1.01
        min_y3 = filtered_data['基差'].min()*0.99               
        main_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=False)
        main_figure.update_xaxes(range=xaxis_range)
        main_figure.update_yaxes(range=[min_y2, max_y2], row=2, col=1, secondary_y=False)
        main_figure.update_yaxes(range=[min_y3, max_y3], row=1, col=1, secondary_y=True)
        return main_figure

    def display_term_structure_figure(self, click_date, spot_price):
        symbol = self.symbol
        df_term = symbol.variety_data 
        if df_term.empty:
             return None, None
        df_term = df_term[df_term['date']==click_date]
        max_open_interest_index= df_term['open_interest'].idxmax()
        # domain_contract = df_term.loc[max_open_interest_index]['symbol']
        df_term = df_term.loc[max_open_interest_index:]
        dominant_months = symbol.symbol_setting['DominantMonths']
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        df_dominant_contract = df_term[df_term['交割月'].isin(dominant_months)]
        # spot_row = pd.DataFrame({
        #     'symbol': ['现货'],
        #     'close': [spot_price],
        #     'settle': [spot_price]
        # })
        # df_dominant_contract = pd.concat([spot_row, df_term])        
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
                                             marker=dict(color=color_flag, opacity=0.6))
        term_fig = go.Figure()
        # term_fig.add_trace(spot_figure)
        term_fig.update_xaxes(linecolor='gray', tickfont=dict(color='gray'))
        term_fig.update_yaxes(linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1)              
        term_fig.add_trace(future_figure)
        max_y = df_dominant_contract['settle'].max() * 1.01
        min_y = df_dominant_contract['settle'].min() * 0.99        
        current_date = click_date.strftime('%Y-%m-%d')
        # term_fig.add_hline(y=spot_price)
        term_fig.update_layout(yaxis_range=[min_y,max_y],
                               title='期限结构:'+current_date,
                               height=120,
                               margin=dict(l=0, r=0, t=30, b=0),
                               plot_bgcolor='White',                   
                               showlegend=False)
        term_fig.update_xaxes(showgrid=False)
        term_fig.update_yaxes(showgrid=False)
        return term_fig, df_dominant_contract, trade_flag

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
        # colors = ['rgba(239,181,59,1.0)', 'rgba(84,134,240,0.5)', 'rgba(105,206,159,0.5)']
        colors = px.colors.qualitative.Pastel
        cross_term_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.05)
        # cross_term_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, shared_xaxes=True, vertical_spacing=0.02)
        row = 1
        df_multi_term = pd.DataFrame()
        profit_loss = {}
        for symbol_name in domain_contract['symbol']:
            df = df_term[df_term['symbol']==symbol_name][['date', 'close']]
            delivery_date = df['date'].max()    
            last_trading_day = delivery_date.replace(day=1)
            if last_trading_day <= click_date:
                last_trading_day = delivery_date #TODO: 替换为交割月的前一个有效交易日
            symbol_figure = go.Scatter(x=df['date'], y=df['close'], name=symbol_name, marker_color=colors[row-1])
            cross_term_figure.update_xaxes(linecolor='gray', tickfont=dict(color='gray'), row=row, col=1)
            cross_term_figure.update_yaxes(linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1, row=row, col=1)            
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
                                        plot_bgcolor='White',     
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
        cross_term_figure.update_annotations(dict(
            x=0,  # x=0 表示最左边
            xanchor='left',  # 锚点设置为左边
            xref="paper",  # 位置参考整个画布的宽度
            yref="paper",  # 位置参考整个画布的高度
            font=dict(size=12)  # 可选的字体大小设置
        ))              
        return cross_term_figure, profit_loss

blank_content = html.Div([
    html.Div(id='methods-navlink'),
    dmc.SegmentedControl(id='segmented-variety-switcher', data=[]),
    dmc.Select(id='variety-select'),
    dmc.Modal(id='modal-chart-config'),
    html.I(id='config-button'),
    dmc.Button(id='close-button'),
    dcc.Graph(id='main-figure-placeholder'),
    dmc.CheckboxGroup([], id='show-indexs'),
    dmc.RadioGroup([], id="price-type"),
    dmc.CheckboxGroup([],id='mark-spot-months'),
    # dmc.CheckboxGroup(id='select-synchronize-index'),
    dmc.Slider(id='trace-back-months'),
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
    Input('show-indexs', 'value'),
    Input('price-type', 'value'),
    Input('mark-spot-months', 'checked'),
    # Input('select-synchronize-index', 'value'),
    Input('trace-back-months', 'value'),
    # allow_duplicate=True
)
def update_graph(select_index_value, radio_future_value, switch_marker_value, look_forward_months_value):   
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
        figure = variety_page.create_figure(select_index_value, radio_future_value, switch_marker_value, select_index_value, look_forward_months_value)
    return figure
    
@callback(
    Output('term-figure-placeholder', 'figure'),
    Output('intertemporal-figure-placeholder', 'figure'),
    # Output('radio_trade_type', 'value'),
    Output('html-analyzing-tags', 'children'),
    Output('html-profit-loss', 'children'),
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
        # 准备分析日志数据
        flag_color ={'Long': 'red', 'Short': 'lime', 'X': 'gray'}
        flag_color2 ={'red': 'red', 'green': 'lime', 'gray': 'gray'}        
        trade_type = {'Long': '单边/跨期做多', 'Short': '单边/跨期做空'}
        basis = clickData['points'][2]['y']
        basis_flag = 'Long' if basis>0 else 'Short'
        click_data = symbol.data_rank[symbol.data_rank['date']==click_date]
        flag_list = variety_page.show_indexs        
        color_list = [click_data[index+'颜色'].iloc[0] for index in flag_list]
        html_analyzing_tags =[
            #     dbc.Badge("远月/近月/交割月", color="primary", className="me-1",id='log_period'),
                dmc.Badge("基差", color=flag_color[basis_flag], id='log_basis'),
                html.Span(" | ")] + [dmc.Badge(flag, color=flag_color2[color_list[index]]) for index, flag in enumerate(flag_list)]        
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
    else:
        return {}, {}, {}, {}

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