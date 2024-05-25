import dash
from dash import html
import dash_mantine_components as dmc
import dash
from dash import html, dcc, callback, Input, Output, State
import dataworks as dw
import plotly.express as px

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

UserData = {}

heat_map_switch = dmc.ChipGroup(
    [dmc.Chip(x, value=x) for x in ["持仓量", "成交量"]],
    value="持仓量",
    id='heat-map-switch'
)

heat_map_panel = dmc.Paper(
    dmc.Stack(
        [
            dmc.Group([
                dmc.Text("市场热力图", id='current-path', w=180),
                heat_map_switch,
            ]),            
            dmc.LoadingOverlay(dcc.Graph(id='market-heatmap-placeholder', config={'displayModeBar': False}),),
        ]
    ),
    shadow="sm",
    radius="xs",
    p="xs",
    withBorder=True,         
)

class MarketOverviewPage:
    def __init__(self) -> None:
        self.main_content = None
        self.heatmap_data = None

    def get_layout(self):
        if self.main_content is None:
            self.main_content = html.Div(
                dmc.Stack(
                    [
                        dmc.Space(h=5),
                        heat_map_panel,
                    ]
                )
            )

        return self.main_content
    
def create_heat_map(self, type):
    """
    创建并返回一个市场热力图的Plotly Express图形对象。
    
    参数:
    - type: 字符串，指定热力图中值的类型（例如：'数量'或'金额'）。
    
    返回值:
    - fig: Plotly Express图形对象，表示市场热力图。
    """
    
    # 检查热力图数据是否已经加载，如果没有则从DataWorks获取
    if self.heatmap_data is None:
        with dw.DataWorks() as dws:
            last_date = dws.get_last_date('dominant')  # 获取最新交易日
            # 构造SQL查询语句，从dominant和symbols表中联接数据
            sql = f"SELECT d.*, s.name, s.chain FROM dominant AS d INNER JOIN symbols AS s ON d.variety = s.code WHERE d.date = '{last_date}'"
            self.heatmap_data = dws.get_data_by_sql(sql)  # 执行SQL查询并将结果存储在成员变量中

    # 使用Plotly Express创建热力图
    fig = px.treemap(self.heatmap_data, path=[px.Constant("市场热力图"), 'chain', 'name'], values=type,
                    color=type, 
                    color_continuous_scale='PuOr',  # 选择颜色渐变方案
                    color_continuous_midpoint=self.heatmap_data[type].min())  # 设置颜色渐变的中点为数据的最小值
    # 更新图形布局，包括边距和颜色轴设置
    fig.update_layout(
        margin = dict(t=25, l=25, r=25, b=25),
        coloraxis_showscale=False,
    )    
    # 更新图形的trace属性，主要是hovertemplate用于鼠标悬停时显示信息
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>%{value}<extra></extra>",
        # customdata=self.heatmap_data['variety'],
        textinfo="label+value+percent parent",
    )        
    return fig  # 返回创建的热力图图形对象

OverviewPages = {}
blank_content = html.Div([
    dmc.NavLink(id="open-chain-page"),
    dmc.NavLink(id="open-variety-page"),
    dmc.NavLink(id="open-all-variety"),
    dmc.ChipGroup(id='heat-map-switch'),
    dcc.Graph(id='market-heatmap-placeholder'),
])
def layout(step=None, **other_unknown_query_strings):
    # if step is None:
    #     return html.Div([
    #         blank_content
    #     ])
    if 'MarketOverview' not in OverviewPages:
        market_overview = MarketOverviewPage()
        OverviewPages['MarketOverview'] = market_overview
        
    return OverviewPages['MarketOverview'].get_layout()

@callback(
    Output('market-heatmap-placeholder', 'figure'),
    Input('heat-map-switch', 'value'),
    allow_duplicate=True
)
def update_heat_map(type):
    """
    根据提供的类型更新热力图。

    参数:
    - type: 需要更新的热力图类型。如果类型为 None，则不进行更新。

    返回值:
    - 如果类型为 None，则返回一个表示没有更新的特殊值。
    - 否则，根据提供的类型创建并返回一个新的热力图。
    """
    # 当类型为 None 时，返回一个表示没有更新的特殊值
    if type is None:
        return dash.no_update
    # 根据提供的类型创建并返回热力图
    return OverviewPages['MarketOverview'].create_heat_map(type)


@callback(
    Output('current-path', 'children'),
    Input('market-heatmap-placeholder', 'clickData'),
    prevent_initial_call=True
)
def heatmap_callback(click_data):
    """
    处理热力图点击事件的回调函数。
    
    参数:
    - click_data: 包含点击事件信息的字典，来自热力图组件的点击事件。
    
    返回值:
    - 如果点击数据有效，则返回点击的路径；如果点击数据无效（None），则不更新状态并返回特殊值dash.no_update。
    """
    if click_data is None:  # 检查点击数据是否为空
        return dash.no_update  # 点击数据为空时，返回no_update以防止状态更新
    
    # 提取并保存点击的路径
    clicked_path = click_data['points'][0]['id']
    UserData['HeatmapClickedPath'] = clicked_path  # 更新用户数据中的热力图点击路径
    
    return clicked_path  # 返回点击的路径

@callback(
    Output("segmented-variety-switcher", "value", allow_duplicate=True),
    Input('open-variety-page', 'n_clicks'),
    # State('market-heatmap-placeholder', 'clickData'),
    # State('current-path', 'children'),
    prevent_initial_call=True
)
def open_variety_page(n_clicks):
    """
    根据用户点击的热力图路径，打开相应的品种页面。
    
    参数:
    - n_clicks: 点击次数，用于触发函数调用，但在此函数中未直接使用。
    
    返回值:
    - 如果用户点击的路径包含品种信息，则返回该品种对应的ID；
    - 如果路径不包含品种信息或UserData中没有HeatmapClickedPath，则不更新界面。
    """
    # 检查UserData中是否记录了热力图的点击路径
    if 'HeatmapClickedPath' not in UserData:
        return dash.no_update
    # 使用DataWorks获取品种ID与名称的映射关系
    with dw.DataWorks() as dws:
        variety_id_name_map, variety_name_id_map = dws.get_variety_map()
    # 获取并解析点击的路径
    clicked_path = UserData['HeatmapClickedPath']
    path_level = clicked_path.split('/')
    levels = len(path_level)
    # 解析出链名称和品种名称
    chain_name = path_level[1] if levels>1 else None
    vareity_name = path_level[2] if levels>2 else None
    # 如果没有解析出品种名称，则不更新界面
    if vareity_name is None:
        return dash.no_update
    # 返回品种名称对应的ID
    return variety_name_id_map[vareity_name]


