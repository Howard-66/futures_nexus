import pandas as pd
import dash
import dash_mantine_components as dmc
from dataworks import DataWorks
from dash import Dash, dcc, html, Input, Output, callback
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from modules.variety import Variety
from modules.chart import ChartManager
from dash_iconify import DashIconify
import global_env as ge

dash.register_page(__name__, path="/variety/basis", title='Futures Nexus: 基本面分析')

variety_page_maps = {}
active_variety_page = None

quant_tags = html.Div([
    dmc.Text('量化分析标签', className="primary_content",),
    html.Div(
        html.Span(
            id='html-analyzing-tags'
        ),    
    ),
])

term_sturcture_panel = html.Div([
    dmc.Text('期限结构', className="primary_content",),
    dcc.Graph(figure={}, id='term-figure-placeholder', config={'displayModeBar': False}),
])

cross_term_panel = html.Div(
    [
        dmc.Text('跨期价差分析', className="primary_content",),
        dcc.Graph(figure={}, id='intertemporal-figure-placeholder', config={'displayModeBar': False}),
    ]
)

analyzing_log = html.Div([
    dmc.Text('盈利-风险测算', className="primary_content",),
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
            term_sturcture_panel,
            shadow="sm",
            radius="xs",
            p="xs",
            withBorder=True,                           
        ),
        # 跨期分析图表
        dmc.Paper(
            cross_term_panel,
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
        self.main_content = None
        symbol = Variety(name)
        symbol.load_data()        
        spot_trading_months = symbol.symbol_setting.get('SpotMonths', 2)
        symbol.get_spot_months(spot_trading_months)
        # symbol.get_spot_months() # TODO
        with DataWorks() as dws:
            symbol.variety_data = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id)
            symbol.variety_data['date'] = pd.to_datetime(symbol.variety_data['date'], format='ISO8601')
            self.chart_manager = ChartManager(symbol)
            self.chart_manager.load_indicators()
            self.look_forward_months = 0
            # self.main_figure = None
            self.on_layout = False
            self.show_indexs = None
            # self.future_type = ''
            # 获取用户设置
            self.user_json='setting/user.json'
            user_setting = dws.load_json_setting(self.user_json)
        if symbol.id not in user_setting['Variety']:
            user_setting['Variety'][symbol.id] = {}
            # dws.save_json_setting(self.user_json, user_setting)        
        self.symbol = symbol
        self.user_setting = user_setting  
        self.main_figure = None
 
    def create_analyzing_layout(self):
        all_fields = self.chart_manager.sub_list
        if 'ShowIndexs' in self.user_setting['Variety'][self.symbol.id]:
            show_fields = self.user_setting['Variety'][self.symbol.id]['ShowIndexs']
        else:
            show_fields = all_fields           
        left_panel = dmc.Stack(
            [
                # 图表配置面板
                dmc.Space(h=2),
                dmc.Paper(
                    dmc.Group(
                        [
                            dmc.ActionIcon(
                                DashIconify(icon="ri:stock-line", width=20),
                                variant="subtle",
                            ),
                            dmc.Popover(
                                [
                                    dmc.PopoverTarget(
                                        dmc.Button("指标", leftSection=DashIconify(icon="material-symbols-light:table-chart-view-outline", width=20), variant='subtle', size='sm')),
                                    dmc.PopoverDropdown(
                                        [
                                            dmc.CheckboxGroup(
                                                id="show-indicators",
                                                label="选择要显示的指标",
                                                mb=10,
                                                children=dmc.Stack(
                                                    [dmc.Checkbox(label=l, value=l) for l in all_fields] + 
                                                    [
                                                        dmc.Group(
                                                            [
                                                                dmc.Text('指标回溯周期', size='sm'),
                                                                dmc.Select(
                                                                    size='sm',
                                                                    data=[
                                                                        {'label': '6个月', 'value': "120"},
                                                                        {'label': '1年', 'value': "240"},
                                                                        {'label': '2年', 'value': "480"},
                                                                        {'label': '3年', 'value': "720"},
                                                                        {'label':'5年', 'value': "1200"},
                                                                        {'label':'全部', 'value': "0"}],
                                                                    value="240",
                                                                    id='traceback-window',
                                                                    style={'width': 80}
                                                                ),  
                                                            ]
                                                        )                                                  
                                                    ],
                                                    mt=10,
                                                ),
                                                value=show_fields,
                                            ),
                                        ]
                                    )
                                ],
                                width=300,
                                position="bottom-start",
                                withArrow=True,
                                arrowPosition="center",
                                trapFocus=True,
                                shadow="sm",                            
                            ),
                            # dmc.Divider(orientation='vertical'),
                            # dmc.Text("价格类型:", size='xs'),
                            # dmc.Select(
                            #     size='xs',
                            #     data=[
                            #         {'label': '主力合约', 'value': '主力合约'},
                            #         {'label': '近月合约', 'value': '近月合约'}],
                            #     value='主力合约',
                            #     id='price-type',
                            #     style={'width': 100}
                            # ),
                            dmc.Divider(orientation='vertical'),
                            dmc.ActionIcon(
                                DashIconify(icon="iconamoon:zoom-in-light", width=20),
                                variant="subtle",
                            ),
                            dmc.ActionIcon(
                                DashIconify(icon="iconamoon:zoom-out-light", width=20),
                                variant="subtle",
                            ),
                            dmc.Divider(orientation='vertical'),
                            dmc.Switch(label="现货交易月", id="mark-spot-months", checked=True, labelPosition="left", radius="lg", size='xs'),            
                            dmc.Divider(orientation='vertical'),
                            dmc.ActionIcon(
                                DashIconify(icon="icon-park-outline:notebook", width=20),
                                variant="subtle",
                            ),
                            dmc.ActionIcon(
                                DashIconify(icon="icon-park-outline:order", width=20),
                                variant="subtle",
                            ),
                            dmc.ActionIcon(
                                DashIconify(icon="iconoir:long-arrow-right-up", width=20),
                                variant="subtle",
                            ),
                            dmc.ActionIcon(
                                DashIconify(icon="iconoir:long-arrow-right-down", width=20),
                                variant="subtle",
                            ),
                        ],
                        gap=2,
                    ),
                    shadow="xs",
                    radius="xs",
                    p=0,
                    withBorder=False,
                    className="background_container",
                ),
                # 图表面板
                dmc.LoadingOverlay(
                    id='basis-figure-loading',
                    visible=True,
                    overlayProps={"radius": "sm", "blur": 2},
                ),
                dcc.Graph(id='basis-figure', config={'displayModeBar': False}, style={'height': '100%'}),
            ],
            gap="xs",
            style={'height': ge.MainContentHeight},
        )              
        layout = dmc.Grid([
                    # 左侧面板
                    dmc.GridCol(left_panel, span=9),
                    # 右侧面板
                    dmc.GridCol(right_panel, span=3)
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
            # self.main_content.children[0].children[0].children.children[1].children[1].value=self.show_indexs
            layout = self.main_content
        self.on_layout = True
        return layout
    
    def create_figure(self, indicator_list, look_forward_months):                
        symbol = self.symbol
        if indicator_list != self.show_indexs:
            self.user_setting['Variety'][symbol.id]['ShowIndexs'] = indicator_list
            with DataWorks() as dws:
                dws.save_json_setting(self.user_json, self.user_setting)    
            self.show_indexs = indicator_list
        if look_forward_months != self.look_forward_months:
            self.chart_manager.calculate_indicators()
        self.look_forward_months = look_forward_months
        # show_symbol_data = symbol.symbol_data.iloc[-SHOW_CHART_NUMBERS:]        
        # show_data_rank = symbol.data_rank.iloc[-SHOW_CHART_NUMBERS:]
        self.chart_manager.plot()
        self.chart_manager.update_figure()
        self.main_figure = self.chart_manager.main_figure  
        return self.main_figure

    def update_yaxes(self, xaxis_range):
        pass

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
            color_flag = ge.SecondaryShortColor
            trade_flag = 'Short'
        elif all(diff<0):
             color_flag = ge.SecondaryLongColor
             trade_flag = 'Long'
        else:
            color_flag = ge.PrimaryNeutralColor
            trade_flag = 'X'
        # print(click_date, type(click_date),  df_term)
        # spot_figure =go.Scatter(x=spot_row['symbol'], y=spot_row['settle'], stackgroup='one',mode='markers',
                                # fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.2)',
                                # marker=dict(color='rgb(0, 123, 255)', opacity=1))
        future_figure = go.Scatter(x=df_term['symbol'], y=df_term['settle'], stackgroup='one', mode='markers',
                                             fill='tozeroy', fillcolor=color_flag,
                                             marker=dict(color=color_flag, opacity=0.6))
        term_fig = go.Figure()
        # term_fig.add_trace(spot_figure)
        term_fig.update_xaxes(linecolor='gray', tickfont=dict(color='gray'))
        term_fig.update_yaxes(linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1)              
        term_fig.add_trace(future_figure)
        max_y = df_term['settle'].max() * 1.01
        min_y = df_term['settle'].min() * 0.99        
        current_date = click_date.strftime('%Y-%m-%d')
        # term_fig.add_hline(y=spot_price)
        term_fig.update_layout(yaxis_range=[min_y,max_y],
                            #    title='期限结构:'+current_date,
                               height=ge.TermStrctureFigureHeight,
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
        specs = [[{"secondary_y": False}] for _ in range(fig_rows)]
        row_widths = [0.1] * (fig_rows - 1) + [0.5]
        subtitles = [''] + list(domain_contract['symbol'][1:])
        # colors = ['rgba(239,181,59,1.0)', 'rgba(84,134,240,0.5)', 'rgba(105,206,159,0.5)']
        colors = px.colors.qualitative.Pastel
        cross_term_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.05)
        row = 1
        df_multi_term = pd.DataFrame()
        profit_loss = {}
        filter_data = df_term[(df_term['date'] >= start_date) & (df_term['date'] <= end_date)]
        for symbol_name in domain_contract['symbol']:
            # df = df_term[df_term['symbol']==symbol_name][['date', 'close']]
            df = filter_data[filter_data['symbol']==symbol_name][['date', 'close']]
            if row==1:
                max_y = df['close'].max()*1.01
                min_y = df['close'].min()*0.99
            delivery_date = df['date'].max()    
            last_trading_day = delivery_date.replace(day=1)
            if last_trading_day <= click_date:
                last_trading_day = delivery_date #TODO: 替换为交割月的前一个有效交易日
            symbol_figure = go.Scatter(x=df['date'], y=df['close'], name=symbol_name, mode='lines', line=dict(color=colors[row-1]))
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
        # filtered_data = df_term[(df_term['date'] >= start_date) & (df_term['date'] <= end_date)]
        # # 计算 y 轴的最大值和最小值
        # max_y = filtered_data['close'].max()*1.01
        # min_y = filtered_data['close'].min()*0.99
        cross_term_figure.update_layout(
                                        height=ge.CrossTermFigureHeight,
                                        margin=dict(l=0, r=0, t=20, b=0),
                                        plot_bgcolor='White',     
                                        hovermode='x unified',              
                                        showlegend=False)
        cross_term_figure.update_xaxes(showgrid=False,
                                    dtick="M1",
                                    ticklabelmode="instant",   # instant  period
                                    tickformat="%m\n%Y",
                                    rangebreaks=[dict(values=self.symbol.trade_breaks)],
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
    dcc.Graph(id='basis-figure'),
    dmc.CheckboxGroup([], id='show-indicators'),
    # dmc.RadioGroup([], id="price-type"),
    dmc.CheckboxGroup([],id='mark-spot-months'),
    # dmc.CheckboxGroup(id='select-synchronize-index'),
    dmc.Slider(id='traceback-window'),
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
    Output('basis-figure', 'figure'),
    Output("basis-figure-loading", "visible"),
    Input('show-indicators', 'value'),
    # Input('price-type', 'value'),
    # Input('mark-spot-months', 'checked'),
    # Input('select-synchronize-index', 'value'),
    Input('traceback-window', 'value'),
    # allow_duplicate=True
)
def update_graph(indicator_list, traceback_window):   
    if 'active_variety' not in variety_page_maps:
        return dash.no_update, dash.no_update
    variety_page = variety_page_maps['active_variety']
    if variety_page.on_layout and variety_page.main_figure is not None:
        figure = variety_page.main_figure
        variety_page.on_layout = False
    else:
        symbol = variety_page.symbol
        # symbol_chain = variety_page.symbol_chain
        # df_profit = symbol.get_profits(radio_future_value, symbol_chain)    
        figure = variety_page.create_figure(indicator_list, int(traceback_window))
    return figure, False
    
@callback(
    Output('term-figure-placeholder', 'figure'),
    Output('intertemporal-figure-placeholder', 'figure'),
    # Output('radio_trade_type', 'value'),
    Output('html-analyzing-tags', 'children'),
    Output('html-profit-loss', 'children'),
    Input('basis-figure', 'clickData'),
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
        # trade_type = {'Long': '单边/跨期做多', 'Short': '单边/跨期做空'}
        # basis = clickData['points'][2]['y']
        # basis_flag = 'Long' if basis>0 else 'Short'

        # show_data_rank = symbol.data_rank.iloc[-SHOW_CHART_NUMBERS:]
        # click_data = show_data_rank[show_data_rank['date']==click_date]
        flag_list = variety_page.show_indexs        
        # color_list = [click_data[index+'颜色'].iloc[0] for index in flag_list]

        color_list = variety_page.chart_manager.get_indicator_data(display_date, flag_list, 'color')
        # html_analyzing_tags =[
        #     #     dbc.Badge("远月/近月/交割月", color="primary", className="me-1",id='log_period'),
        #         dmc.Badge("基差", color=flag_color[basis_flag], id='log_basis'),
        #         html.Span(" | ")] + [dmc.Badge(flag, color=flag_color2[color_list[index]]) for index, flag in enumerate(flag_list)]        
        html_analyzing_tags =[dmc.Badge(flag, color=color_list[index]) for index, flag in enumerate(flag_list)]           
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
        head = dmc.TableThead(
            dmc.TableTr(
                [dmc.TableTh(col) for col in columns]
            )
        )
        rows = [dmc.TableTr([dmc.TableTd(cell) for cell in row]) for row in values]      
        # caption = dmc.TableCaption("盈利/风险测算")
        html_profit_loss = dmc.Table([head, dmc.TableTbody(rows)], striped=True, highlightOnHover=True, withTableBorder=False, withColumnBorders=False, captionSide="top")
        return term_fig, cross_term_figure, html_analyzing_tags, html_profit_loss
    else:
        return {}, {}, {}, {}

@callback(
    Output(component_id='basis-figure', component_property='figure', allow_duplicate=True),
    Input('basis-figure', 'relayoutData'),
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