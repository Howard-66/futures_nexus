import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dataworks import DataWorks

SIDEBAR_WIDTH = 200
PAGE_BACKGROUND_COLOR = "#f5f5f5"

app = Dash(__name__, 
           use_pages=True,       
           prevent_initial_callbacks='initial_duplicate')

quick_access = html.Div(
    style={"width": SIDEBAR_WIDTH, "height": "auto"},
    children=[
        dmc.NavLink(
            label="板块品种",
            icon=DashIconify(icon="akar-icons:link-chain", width=24),
            childrenOffset=28,
            children=[
                dmc.NavLink(label="First child link"),
                dmc.NavLink(label="Second child link"),
            ],
            variant="subtle",
            opened=True,
            active=True,
        ),
        dmc.NavLink(
            label="自选品种",
            icon=DashIconify(icon="fluent-mdl2:favorite-list", width=24),
            childrenOffset=28,            
            children=[
                dmc.NavLink(label="First child link", variant="subtle"),
                dmc.NavLink(label="Second child link"),
                dmc.NavLink(label="Third child link"),
            ],
            variant="subtle",
            opened=True,
            active=True,
        ),
    ],
)

def create_analysis_stepper(variety_id):
    analysis_stepper = dmc.Stepper(
        id="analysis-stepper",
        orientation="vertical",
        iconSize=36,
        active=0,
        children=[
            dmc.StepperStep(
                label=dmc.Anchor("基本面量化分析", href=f"/variety/basis?variety_id={variety_id}", id="basis-step"),
                description="基差-库存-利润模型分析",
                children=[
                    dmc.Divider(variant="solid", label="快速功能", labelPosition="center"),
                    dmc.Space(h=10),
                    dmc.NavLink(label="图表设置", id="chart-config", icon=DashIconify(icon="tabler:settings")),
                    dmc.NavLink(label="主成分分析", variant="subtle", id="pca-analysis", icon=DashIconify(icon="ri:pie-chart-2-line")),
                    dmc.NavLink(label="AI交易建议", variant="subtle", id="drl-analysis", icon=DashIconify(icon="prime:microchip-ai")),
                ],
            ),
            dmc.StepperStep(
                label=dmc.Anchor("AI模型分析", href=f"/variety/drl?variety_id={variety_id}", id="drl-step"),
                description="通过深度强化学习给出操作建议和价格预测",
                children=[
                    dmc.Text("周期性分析"),
                ],
            ),            
            dmc.StepperStep(
                label=dmc.Anchor("周期性分析", href=f"/variety/cycle?variety_id={variety_id}", id="cycle-step"),
                description="基于ARIMA模型的周期性分析",
                children=[
                    dmc.Text("AI模型分析"),
                ],
            ),
            dmc.StepperStep(
                label=dmc.Anchor("套利分析", href=f"/variety/arb?variety_id={variety_id}", id="arb-step"),
                description="跨期、跨品种套利分析",
                children=[
                    dmc.Text("套利分析"),
                ],
            ),        
            dmc.StepperStep(
                label=dmc.Anchor("技术分析", href=f"/variety/tech?variety_id={variety_id}", id="tech-step"),
                description="基于技术指标、缠论分析",
                children=[
                    dmc.Text("技术分析"),
                ],
            ),        
            dmc.StepperStep(
                label=dmc.Anchor("综合决策", href=f"/variety/trade?variety_id={variety_id}", id="basis-step"),
                description="综合上述分析结论，制定交易计划和决策",
                icon=DashIconify(icon="fluent-mdl2:decision-solid", width=20),
                children=[
                    dmc.Text("综合决策"),
                ],
            ),
        ],
    )
    return analysis_stepper

analysis_stepper_placeholder = dmc.Stepper(
    [],
    id="analysis-stepper",
    active=0
)

# 侧边栏-标签切换
sidebar_tabs =dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.Tab("分析", value="analysis"),
                dmc.Tab("板块", value="chain"),
                dmc.Tab("自选", value="favorite"),
            ]
        ),
        dmc.TabsPanel(analysis_stepper_placeholder, value="analysis", p="md", id="sidebar-analysis-tab"),
        dmc.TabsPanel("", value="chain", id="sidebar-chain-tab"),
        dmc.TabsPanel(quick_access, value="favorite" ,p="md", id="sidebar-favorite-tab"),
    ],
    value="analysis",
)

# 侧边栏
sidebar = dmc.Paper(
    [
        sidebar_tabs
    ],
    shadow="sm",
    # p="xl",
    h=1300,
    withBorder=False,
)

navbar = dmc.Navbar(
    [
        sidebar
    ],
    p="sm",
    width={"base": SIDEBAR_WIDTH+50},
    height=1300,
    withBorder=False,
    fixed=True,
    style={"backgroundColor": PAGE_BACKGROUND_COLOR},
)

# 头部菜单
header = dmc.Header(
    [        
        dmc.Paper(
            dmc.Container(
                children=[
                    dmc.Group(
                        children=[
                            DashIconify(icon="simple-icons:bitcoincash", width=24, color="gray"),
                            dmc.Text("Futures Nexus", color="gray"),
                            dmc.Space(w=60),
                            dmc.Select(searchable=True, clearable=True, id="variety-search",
                                       placeholder="输入品种代号", nothingFound="未找到品种",),
                            # dmc.Button("Search", variant="outline", leftIcon=DashIconify(icon="wpf:search", width=20)),
                            # dmc.NavLink(variant="subtle", icon=DashIconify(icon="wpf:search", width=20)),
                            dmc.Space(w=60),
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("市场全景", variant="subtle", leftIcon=DashIconify(icon="uiw:global", width=20))),               
                                ],
                            ),                             
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("金属", variant="subtle", leftIcon=DashIconify(icon="icon-park-outline:heavy-metal", width=24))),
                                    dmc.MenuDropdown(
                                        children=[                                    
                                            dmc.MenuItem("钢铁产业链", href="/chain/overview?chain_id=black_metal", icon=DashIconify(icon="tabler:ironing-steam", width=20)),
                                            dmc.MenuItem("贵金属产业链", icon=DashIconify(icon="ant-design:gold-outlined", width=20)),
                                            dmc.MenuItem("铜产业链", icon=DashIconify(icon="mingcute:copper-coin-line", width=20)),
                                            dmc.MenuItem("铝产业链", icon=DashIconify(icon="file-icons:silverstripe", width=20)),
                                        ],
                                    ),                       
                                ],
                            ),
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("能源", variant="subtle", leftIcon=DashIconify(icon="material-symbols:energy-savings-leaf-outline", width=24))),
                                    dmc.MenuDropdown(
                                        children=[                                    
                                            dmc.MenuItem("动力煤产业链", icon=DashIconify(icon="mdi:charcoal-outline", width=20)),
                                            dmc.MenuItem("石油产业链", icon=DashIconify(icon="lets-icons:oil", width=20)),
                                            dmc.MenuItem("原油产业链", icon=DashIconify(icon="mdi:boil-point-outline", width=20)),
                                        ],
                                    ),                       
                                ],
                            ),                    
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("化工", variant="subtle", leftIcon=DashIconify(icon="mdi:chemical-weapon", width=24))),
                                    dmc.MenuDropdown(
                                        children=[                                    
                                            dmc.MenuItem("化工产业链", icon=DashIconify(icon="healthicons:chemical-burn-outline", width=20)),
                                            dmc.MenuItem("沥青产业链", icon=DashIconify(icon="arcticons:asphalt-8", width=20)),
                                            dmc.MenuItem("橡胶产业链", icon=DashIconify(icon="tabler:rubber-stamp", width=20)),
                                        ],
                                    ),                       
                                ],
                            ),          
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("农产品", variant="subtle", leftIcon=DashIconify(icon="ic:outline-agriculture", width=24))),
                                    dmc.MenuDropdown(
                                        children=[                                    
                                            dmc.MenuItem("菜籽油产业链", icon=DashIconify(icon="mdi:seedling-outline", width=20)),
                                            dmc.MenuItem("大豆产业链", icon=DashIconify(icon="ph:coffee-bean-bold", width=20)),
                                            dmc.MenuItem("糖产业链", icon=DashIconify(icon="ep:sugar", width=20)),
                                            dmc.MenuItem("小麦产业链", icon=DashIconify(icon="lucide:wheat", width=20)),
                                            dmc.MenuItem("玉米产业链", icon=DashIconify(icon="tdesign:corn", width=20)),
                                            dmc.MenuItem("棕榈油产业链", icon=DashIconify(icon="ph:tree-palm", width=20)),
                                            dmc.MenuItem("生猪产业链", icon=DashIconify(icon="clarity:piggy-bank-line", width=20)),
                                        ],
                                    ),                       
                                ],
                            ),                                   
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("自选", variant="subtle", leftIcon=DashIconify(icon="mdi:favorite-settings-outline", width=24))),               
                                ],
                            ),                       
                            dmc.Menu(                    
                                [
                                    dmc.MenuTarget(dmc.Button("设置", variant="subtle", leftIcon=DashIconify(icon="icon-park-outline:config", width=24))),
                                    dmc.MenuDropdown(
                                        children=[                                    
                                            dmc.MenuItem("数据管理", icon=DashIconify(icon="icon-park-outline:data-switching", width=20)),
                                            dmc.MenuItem("品种管理", icon=DashIconify(icon="carbon:data-class", width=20)),
                                            dmc.MenuItem("通用设置", icon=DashIconify(icon="grommet-icons:configure", width=20)),
                                        ],
                                    ),                       
                                ],
                            ),                                                       
                        ],
                        # position="apart",
                    ),
                ],
                fluid=True,
                # style={"height": "100px"},
            ),
            shadow="sm",
            radius="xs",
            p="xs",
            withBorder=True,
        )        
    ], 
    height="auto", 
    fixed=True,
    # style={"backgroundColor": "#9c86e2"}
)

footer = dmc.Footer(
    height=30, children=[dmc.Text("Company Logo")], style={"backgroundColor": "#9c86e2"}
)

style = {
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['indigo'][4]}",
    "textAlign": "center",
}

# 品种标签栏
seg_variety = dmc.SegmentedControl(
    id="segmented-variety-switcher",
    value="market_overview",    
    data=[
        {"value": "market_overview", "label": "市场全景"},
    ],
    # mt=10,
    color="#E0E0E0",
    style={"backgroundColor": PAGE_BACKGROUND_COLOR}
),

# 品种工具栏
tab_bar = dmc.Grid(
    [
        dmc.Col(seg_variety, span="auto"),
        dmc.Col(
            dmc.ActionIcon(DashIconify(icon="carbon:close-outline"), id="button-remove-tab", variant="subtle", color="blue", size=36, radius="xs"),                    
            xs=0.35),
        dmc.Col(                  
            dmc.ActionIcon(DashIconify(icon="tabler:settings"), id="button-methond-config", variant="subtle", color="blue", size=36, radius="xs"),
            xs=0.35),           
    ],
    # style={"backgroundColor": PAGE_BACKGROUND_COLOR},
)

# 主内容框架
main_context = dmc.Grid(
    children=[        
        dmc.Col(navbar, span=1),
        dmc.Col(
            dmc.Stack(
                children=[
                    dmc.Space(h=50),                    
                    tab_bar,
                    dmc.Divider(variant="solid"),
                    dash.page_container,
                ],
                spacing=0,
                p=5
            ),
        offset=0.45,
        span="auto"),
    ],
    gutter="5",
    style={"backgroundColor": PAGE_BACKGROUND_COLOR},
)

app.layout = html.Div(
    [
        # dcc.Location(id="url", refresh=False),
        dmc.MantineProvider(
            dmc.Stack(
                children=[
                    header,
                    main_context,
                    # footer,
                ],
                spacing=4,
            ),            
            # theme={"colorScheme": "dark"},
            withGlobalStyles=True,
        ),
    ],
)

from urllib.parse import urlparse, parse_qs
# 特殊转义页面
spec_pages = {
    "market_overview": "/",
    "black_metal": "/chain/black_metal",
}

global_var = {
    "pre_active_tab": None
}

@app.callback(
    Output("analysis-stepper", "active"),
    Input("_pages_location", "pathname"),
    Input("_pages_location", "search"),
    prevent_initial_call=True,
)
def update_stepper(pathname, search):
    analysis_maps = {
        "/variety/basis": 0,
        "/variety/drl": 1,
        "/variety/cycle": 2,
        "/variety/arb": 3,
        "/variety/tech": 4,
        "/variety/trade": 5,
    }
    if pathname in analysis_maps:
        return analysis_maps[pathname]
    else:
        return dash.no_update

# 品种搜索框回调函数
@app.callback(
    Output("segmented-variety-switcher", "value"),
    Output("variety-search", "data"),
    Input("variety-search", "value"),
    State("variety-search", "data")
    # prevent_initial_call=True,
)
def variety_search_callback(value, data):
    if data is None:
        dws = DataWorks()
        variety_id_name_map, variety_name_id_map = dws.get_variety_map()        
        vareity_search_list = []
        for variety_id, variety_name in variety_id_name_map.items():
            vareity_search_list.append({"value": variety_id, "label": f'{variety_name}({variety_id})'})
        return dash.no_update, vareity_search_list
    if value is None:
        return dash.no_update, dash.no_update
    return value, dash.no_update
    
@app.callback(
    Output("_pages_location", "pathname"),
    Output("_pages_location", "search"),
    Output("sidebar-analysis-tab", "children"),
    Output("segmented-variety-switcher", "data"),
    Input("segmented-variety-switcher", "value"),
    State("segmented-variety-switcher", "data"),
    prevent_initial_call=True
)
def update_variety(to_active_tab, tab_list):    
    if to_active_tab==global_var["pre_active_tab"]:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update    
    contains_active_tab = any(item['value'] == to_active_tab for item in tab_list)
    if contains_active_tab:
        tab_list = dash.no_update   
        if to_active_tab in spec_pages:
            parsed_url = urlparse(spec_pages[to_active_tab])
            pathname = parsed_url.path
            search = parsed_url.query
            # create sidebar in special page
            sidebar_analysis_tab = dash.no_update
        else:
            pathname = "/variety/basis"
            search = f"?variety_id={to_active_tab}"
            sidebar_analysis_tab = create_analysis_stepper(to_active_tab)
    else:
        if to_active_tab in spec_pages:
            parsed_url = urlparse(spec_pages[to_active_tab])
            pathname = parsed_url.path
            search = parsed_url.query
            # create sidebar in special page
            sidebar_analysis_tab = dash.no_update
        else:
            pathname = "/variety/basis"
            search = f"?variety_id={to_active_tab}"
            sidebar_analysis_tab= create_analysis_stepper(to_active_tab)
        dws = DataWorks()
        variety_id_name_map, variety_name_id_map = dws.get_variety_map()
        tab_list.append({"value": to_active_tab, "label": variety_id_name_map[to_active_tab]})
    global_var["pre_active_tab"] = to_active_tab
    return pathname, search, sidebar_analysis_tab, tab_list
    
@app.callback(
    Output("segmented-variety-switcher", "data", allow_duplicate=True),
    Output("segmented-variety-switcher", "value", allow_duplicate=True),
    Input("button-remove-tab", "n_clicks"),
    State("segmented-variety-switcher", "value"),
    State("segmented-variety-switcher", "data"),
    prevent_initial_call=True,
)
def remove_tab(n_clicks, value, data):
    if len(data) <=1:
        return data, value
    select_index = [index for index, item in enumerate(data) if value not in item['value']]
    del data[select_index[0]]
    active_value = data[0]['value']
    return data, active_value

if __name__ == '__main__':
    app.run(debug=True)