import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from pages.chain_overview import chain_page_maps
import components.style as style
from global_service import gs
from dataworks import DataWorks

dash.register_page(__name__, path="/variety/overview")

chart_config = html.Div(
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
    ]
)

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
        symbol_chain = chain_page_maps[self.chain_name].symbol_chain
        symbol = symbol_chain.get_symbol(name)
        symbol.get_spot_months()
        dws = DataWorks()
        # symbol.variety_data = gs.dataworks.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data = dws.get_data_by_symbol(symbol.symbol_setting['ExchangeID'], symbol.id, ['symbol', 'date', 'close', 'volume', 'open_interest', 'settle', 'variety'])
        symbol.variety_data['date'] = pd.to_datetime(symbol.variety_data['date'])
        self.symbol = symbol

    def create_variety_menu(self):
        menu = dbc.Nav(
            [     
                html.I(className="bi bi-gear me-2", style={'font-size': '1.5rem', 'color': 'cornflowerblue'}, id='config-button'),
                dbc.NavLink("基本面分析", href=f"/variety_overview?variety_id={self.variety_name}&chain_id={self.chain_name}", active="exact"),
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
                            dbc.Col(menu),
                            # dbc.Col(index_selector),
                        ],
                    ),
                    dbc.Row(analyzing_layout),
                ],
                style=style.CONTENT_STYLE
            )
            self.main_content = layout
        else:
            layout = self.main_content
        return layout

variety_page_maps = {}

blank_content = html.Div([
    dbc.Modal(id='modal-chart-config'),
    html.I(id='config-button'),
    dbc.Button(id='close-button'),
], style=style.CONTENT_STYLE)

def layout(variety_id=None, chain_id=None, **other_unknown_query_strings):
    if variety_id is None:
        return html.Div([
            dbc.Row(blank_content)
        ])
    sidebar = chain_page_maps[chain_id].sidebar
    if variety_id not in variety_page_maps:
        variety_page = VarietyPage(variety_id, chain_id)
        variety_page_maps[variety_id] = variety_page
    else:
        variety_page = variety_page_maps[variety_id]    
    layout = html.Div([
        dbc.Row(
            [
                dbc.Col(sidebar,),
                dbc.Col(variety_page.get_layout(),)
            ],
        )
    ])

    return layout

@callback(
    Output("modal-chart-config", "is_open"),
    [Input("config-button", "n_clicks"), Input("close-button", "n_clicks")],
    [State("modal-chart-config", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open