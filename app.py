import dash
from dash import Dash, _dash_renderer, dcc, html, callback, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dataworks import DataWorks
import re

_dash_renderer._set_react_version("18.2.0")

HeaderHeight = 70
NavbarWidth = 240
AsideWidth = 300
MainContentHeight = 1250
MainContentPaddingTop = 70
MainContentBGColor = "#f5f5f5"

main_menu = dmc.Group(
    [
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("市场全景", variant="subtle", leftSection=DashIconify(icon="uiw:global", width=20))),               
            ],
        ),                             
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("金属", variant="subtle", leftSection=DashIconify(icon="icon-park-outline:heavy-metal", width=24))),
                dmc.MenuDropdown(
                    children=[                                    
                        dmc.MenuItem("钢铁产业链", href="/chain/overview?chain_id=black_metal", leftSection=DashIconify(icon="tabler:ironing-steam", width=20)),
                        dmc.MenuItem("贵金属产业链", leftSection=DashIconify(icon="ant-design:gold-outlined", width=20)),
                        dmc.MenuItem("铜产业链", leftSection=DashIconify(icon="mingcute:copper-coin-line", width=20)),
                        dmc.MenuItem("铝产业链", leftSection=DashIconify(icon="file-icons:silverstripe", width=20)),
                    ],
                ),                       
            ],
        ),
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("能源", variant="subtle", leftSection=DashIconify(icon="material-symbols:energy-savings-leaf-outline", width=24))),
                dmc.MenuDropdown(
                    children=[                                    
                        dmc.MenuItem("动力煤产业链", leftSection=DashIconify(icon="mdi:charcoal-outline", width=20)),
                        dmc.MenuItem("石油产业链", leftSection=DashIconify(icon="lets-icons:oil", width=20)),
                        dmc.MenuItem("原油产业链", leftSection=DashIconify(icon="mdi:boil-point-outline", width=20)),
                    ],
                ),                       
            ],
        ),                    
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("化工", variant="subtle", leftSection=DashIconify(icon="mdi:chemical-weapon", width=24))),
                dmc.MenuDropdown(
                    children=[                                    
                        dmc.MenuItem("化工产业链", leftSection=DashIconify(icon="healthicons:chemical-burn-outline", width=20)),
                        dmc.MenuItem("沥青产业链", leftSection=DashIconify(icon="arcticons:asphalt-8", width=20)),
                        dmc.MenuItem("橡胶产业链", leftSection=DashIconify(icon="tabler:rubber-stamp", width=20)),
                    ],
                ),                       
            ],
        ),          
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("农产品", variant="subtle", leftSection=DashIconify(icon="ic:outline-agriculture", width=24))),
                dmc.MenuDropdown(
                    children=[                                    
                        dmc.MenuItem("菜籽油产业链", leftSection=DashIconify(icon="mdi:seedling-outline", width=20)),
                        dmc.MenuItem("大豆产业链", leftSection=DashIconify(icon="ph:coffee-bean-bold", width=20)),
                        dmc.MenuItem("糖产业链", leftSection=DashIconify(icon="ep:sugar", width=20)),
                        dmc.MenuItem("小麦产业链", leftSection=DashIconify(icon="lucide:wheat", width=20)),
                        dmc.MenuItem("玉米产业链", leftSection=DashIconify(icon="tdesign:corn", width=20)),
                        dmc.MenuItem("棕榈油产业链", leftSection=DashIconify(icon="ph:tree-palm", width=20)),
                        dmc.MenuItem("生猪产业链", leftSection=DashIconify(icon="clarity:piggy-bank-line", width=20)),
                    ],
                ),                       
            ],
        ),                                   
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("自选", variant="subtle", leftSection=DashIconify(icon="mdi:favorite-settings-outline", width=24))),               
            ],
        ),                       
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("设置", variant="subtle", leftSection=DashIconify(icon="icon-park-outline:config", width=24))),
                dmc.MenuDropdown(
                    children=[                                    
                        dmc.MenuItem("数据管理", leftSection=DashIconify(icon="icon-park-outline:data-switching", width=20)),
                        dmc.MenuItem("品种管理", leftSection=DashIconify(icon="carbon:data-class", width=20)),
                        dmc.MenuItem("通用设置", leftSection=DashIconify(icon="grommet-icons:configure", width=20)),
                    ],
                ),                       
            ],
        ),
    ],
    justify="flex-end",
)

theme_toggle = dmc.ActionIcon(
    [
        DashIconify(
            icon="radix-icons:sun",
            width=25,
            id="light-theme-icon",
        ),
        DashIconify(
            icon="radix-icons:moon",
            width=25,
            id="dark-theme-icon",
        ),
    ],
    variant="transparent",
    color="yellow",
    id="color-scheme-toggle",
    size="lg",
    ms="auto"
)

# 头部菜单
header = dmc.Paper(
    dmc.Grid(
        [
            dmc.GridCol(
                dmc.Group(
                    [
                        dmc.Burger(id="burger-button", opened=True, size="xs", color="blue"),
                        DashIconify(icon="simple-icons:bitcoincash", width=24, color="blue"),
                        dmc.Text("Futures Nexus", c="blue",size="xl"),
                    ],
                    justify="flex-start",
                ),
                span="content",
            ),
            dmc.GridCol(
                main_menu,
                span="auto",
            ),
            dmc.GridCol(
                dmc.Group(
                    [
                        dmc.Space(w=30),
                        dmc.Select(searchable=True, clearable=True, id="variety-search",
                                    placeholder="搜索品种名称/代号", nothingFoundMessage="未找到品种",),
                        dmc.Space(w=30),
                        theme_toggle,
                    ],
                    justify="flex-end",
                    gap="xs",
                ),
                span="content",
            )
        ],
        gutter="xs",
        align="center",
    ),
    shadow="sm",
    radius="xs",
    p="sm",
    withBorder=False,
    # style={"backgroundColor": "#f5f5f5"}
)

quick_access = html.Div(
    style={"width": NavbarWidth, "height": "auto"},
    children=[
        dmc.NavLink(
            label="活跃商品",
            leftSection=DashIconify(icon="akar-icons:link-chain", width=24),
            childrenOffset=28,
            children=[
                dmc.NavLink(label="螺纹钢", href='/variety/basis?variety_id=RB'),
                dmc.NavLink(label="Second child link"),
            ],
            variant="subtle",
            opened=True,
            active=True,
        ),
        dmc.NavLink(
            label="自选品种",
            leftSection=DashIconify(icon="fluent-mdl2:favorite-list", width=24),
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

def create_variety_stepper(variety_id):
    analysis_stepper = dmc.Stepper(
        id="variety-stepper",
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
                    dmc.NavLink(label="图表设置", id="chart-config", leftSection=DashIconify(icon="tabler:settings")),
                    dmc.NavLink(label="主成分分析", variant="subtle", id="pca-analysis", leftSection=DashIconify(icon="ri:pie-chart-2-line")),
                    dmc.NavLink(label="AI交易建议", variant="subtle", id="drl-analysis", leftSection=DashIconify(icon="prime:microchip-ai")),
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

variety_stepper_placeholder = dmc.Stepper(
    [       
    ],
    id="variety-stepper",
    active=0
)

market_stepper_placeholder = dmc.Stepper(
    [
        dmc.StepperStep(
            label=dmc.Anchor("市场热力图", href=f"/?step=heatmap", id="heatmap-step"),
            description="根据持仓量、交易量等指标判断活跃品种",
            icon=DashIconify(icon="carbon:calendar-heat-map", width=20),
            children=[
                dmc.Divider(variant="solid", label="快速功能", labelPosition="center"),
                dmc.Space(h=10),
                dmc.NavLink(label="进入品种页面", id="open-variety-page", leftSection=DashIconify(icon="fluent:open-24-regular")),
                dmc.NavLink(label="进入板块页面", id="open-chain-page", leftSection=DashIconify(icon="akar-icons:link-chain")),
                dmc.NavLink(label="打开板块全部品种", variant="subtle", id="open-all-variety", leftSection=DashIconify(icon="carbon:collapse-all")),
            ],
        ),
        dmc.StepperStep(
            label=dmc.Anchor("基本面气泡图", href=f"/?step=fundment", id="fundment-step"),                
            icon=DashIconify(icon="tdesign:chart-bubble", width=20),
            description="基差-库存-利润象限模型分析",
            children=[
                dmc.Text("基本面气泡图"),
            ],
        ),            
        dmc.StepperStep(
            label=dmc.Anchor("投资雷达", href=f"/?step=radar", id="radar-step"),
            description="根据预设规则捕捉市场异动",
            icon=DashIconify(icon="clarity:radar-line", width=20),
            children=[
                dmc.Text("投资雷达"),
            ],
        ),     
    ],
    id="market-stepper",
    orientation="vertical",
    iconSize=36,
    active=0,
)


# 侧边栏-标签切换
sidebar_tabs =dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.TabsTab("分析", value="analysis"),
                dmc.TabsTab("板块", value="chain"),
                dmc.TabsTab("自选", value="favorite"),
            ]
        ),
        dmc.TabsPanel([market_stepper_placeholder,variety_stepper_placeholder], value="analysis", p="md", id="sidebar-analysis-tab"),
        dmc.TabsPanel("", value="chain", id="sidebar-chain-tab"),
        dmc.TabsPanel(quick_access, value="favorite" ,p="md", id="sidebar-favorite-tab"),
    ],
    value="analysis",
)

navbar = dcc.Loading(    
    dmc.ScrollArea(
        # dmc.Paper(
        [
            sidebar_tabs
        ],
        #     shadow="md",
        #     radius="xs",
        #     p="xs",
        #     style={"height": MainContentHeight},
        #     withBorder=False,        
        # ),
        offsetScrollbars=True,
        type="scroll",
        p="xs",
        style={"height": "100%"},
    ),
)


# 品种标签栏
seg_variety = dmc.SegmentedControl(
    id="page-switch-tabs",
    value="market_overview",    
    data=[
        {"value": "market_overview", "label": "市场全景"},
    ],
    # mt=10,
    # color="#E0E0E0",
    color="blue"
    # style={"backgroundColor": PageBackgroundColor}
),

favorite_toggle = dmc.ActionIcon(
    [
        DashIconify(
            icon="clarity:favorite-line",
            width=25,
            id="add-favorite-icon",
        ),
        DashIconify(
            icon="clarity:favorite-solid",
            width=25,
            id="remove-favorite-icon",
        ),
    ],
    variant="transparent",
    color="yellow",
    id="favorite-toggle",
    size="lg",
    ms="auto"
)

# 品种工具栏
tab_bar = dmc.Grid(
    [
        dmc.GridCol(seg_variety, span="auto"),
        dmc.GridCol(
            dmc.ActionIcon(DashIconify(icon="carbon:close-outline"), id="button-remove-tab", variant="subtle", color="blue", size=36, radius="xs"), span="content"),
        dmc.GridCol(                  
            dmc.ActionIcon(
                [
                    DashIconify(icon="clarity:favorite-line", id="add-favorite-icon",),
                    # DashIconify(icon="clarity:favorite-solid", id="remove-favorite-icon",),
                ],
                variant="transparent",
                color="yellow",
                id="favorite-toggle",
                size=36,
                ms="auto"
            ),
        span="content"),           
    ],
    # style={"backgroundColor": PageBackgroundColor},
)


page_content = dmc.Stack(
    children=[
        tab_bar,
        dmc.Divider(variant="solid"),                    
        dash.page_container,
    ],
    gap=0,
    justify="flex-start",
    align="stretch",
    # p=5
)

stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

app = Dash(
    __name__, 
    use_pages=True,       
    prevent_initial_callbacks='initial_duplicate',
    external_stylesheets=stylesheets,
    suppress_callback_exceptions=True,
)


app_shell = dmc.AppShell(
    [
        dmc.AppShellHeader(header, withBorder=False, style={"backgroundColor": MainContentBGColor}),
        dmc.AppShellNavbar(navbar, withBorder=True),
        dmc.AppShellAside("Aside", withBorder=True),
        dmc.AppShellMain(page_content, pt=MainContentPaddingTop),
        # dmc.AppShellFooter("Footer")
    ],
    header={"height": HeaderHeight},
    padding="xl",
    navbar={
        "width": NavbarWidth,
        "breakpoint": "md",
        "collapsed": {"desktop": False, "mobile": True},
        "opened": True,
    },
    aside={
        "width": AsideWidth,
        "breakpoint": "xl",
        "collapsed": {"desktop": True, "mobile": True},
        "opened": False,
    },
    id="app-shell",
)

app.layout = dmc.MantineProvider(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        app_shell
    ],
    id="mantine-provider",
    forceColorScheme="light",
)


@callback(
    Output("app-shell", "navbar"),
    Input("burger-button", "opened"),
    State("app-shell", "navbar"),
)
def navbar_is_open(opened, navbar):
    navbar["collapsed"] = {"desktop": not opened}
    return navbar



clientside_callback(
    """
    function(data) {
        return data
    }
    """,
    Output("mantine-provider", "forceColorScheme"),
    Input("theme-store", "data"),
)


clientside_callback(
    """
    function(n_clicks, data) {
        return data === "dark" ? "light" : "dark";
    }
    """,
    Output("theme-store", "data"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)


from urllib.parse import urlparse, parse_qs
# 特殊转义页面
spec_pages = {
    "market_overview": "/",
    "black_metal": "/chain/black_metal",
}

global_var = {
    "pre_active_tab": None # 上一个激活的tab
}

@app.callback(
    Output("variety-stepper", "active"),
    Input("_pages_location", "pathname"),
    Input("_pages_location", "search"),
    prevent_initial_call=True,
)
def update_stepper(pathname, search):
    """
    根据给定的路径名称更新步进器的状态。

    参数:
    - pathname: 字符串，表示需要更新的路径名称。
    - search: 用于搜索的关键词，本函数未使用此参数。

    返回值:
    - 如果给定的pathname存在于analysis_maps中，返回对应的索引值。
    - 如果pathname不存在于analysis_maps中，返回dash.no_update（表示不进行更新）。
    """
    # 初始化分析映射，将特定路径名称映射到索引值
    analysis_maps = {
        "/variety/basis": 0,
        "/variety/drl": 1,
        "/variety/cycle": 2,
        "/variety/arb": 3,
        "/variety/tech": 4,
        "/variety/trade": 5,
    }
    # 检查pathname是否存在于映射中并返回对应的索引值，否则返回不更新的标记
    if pathname in analysis_maps:
        return analysis_maps[pathname]
    else:
        return dash.no_update

# 品种搜索框回调函数
@app.callback(
    Output("page-switch-tabs", "value", allow_duplicate=True),
    Output("variety-search", "data"),
    Input("variety-search", "value"),
    State("variety-search", "data")
    # prevent_initial_call=True,
)
def variety_search_callback(value, data):
    """
    处理品种搜索回调请求。
    
    当data参数为None时，从DataWorks获取品种ID与名称的映射关系，并将这些映射转换为可供选择的列表格式；
    当value参数为None时，不进行任何操作，返回no_update；
    当data和value都不为None时，将value作为返回值，不更新数据列表。
    
    :param value: 用户输入的搜索值。
    :param data: 前一次调用的返回数据。
    :return: 根据不同的情况返回dash.no_update或者搜索结果列表。
    """
    if data is None:
        # 初始化DataWorks上下文，获取品种ID与名称的映射
        with DataWorks() as dws:
            variety_id_name_map, variety_name_id_map = dws.get_variety_map()
        
        # 根据ID和名称映射，生成前端可使用的选项列表
        vareity_search_list = []
        for variety_id, variety_name in variety_id_name_map.items():
            vareity_search_list.append({"value": variety_id, "label": f'{variety_name}({variety_id})'})
        
        # 返回更新后的选项列表，不更新value
        return dash.no_update, vareity_search_list
    if value is None:
        # 当value为None时，既不更新选项列表，也不更新value
        return dash.no_update, dash.no_update
    # 当data和value不为None时，更新value，不更新选项列表
    return value, dash.no_update

@app.callback(
    Output("page-switch-tabs", "value", allow_duplicate=True),
    Input("url", "pathname"),
    Input("url", "search"),
    prevent_initial_call=True
)
def redir_update_variety(pathname, search):
    match = re.search(r'variety_id=([A-Za-z]+)', search)
    print(search, match)
    if match:
        return match.group(1)
    return dash.no_update

@app.callback(
    Output("_pages_location", "pathname"),
    Output("_pages_location", "search"),
    Output("sidebar-analysis-tab", "children"),
    Output("page-switch-tabs", "data", allow_duplicate=True),
    Input("page-switch-tabs", "value"),
    State("page-switch-tabs", "data"),
    prevent_initial_call=True
)
def update_variety(to_active_tab, tab_list):  
    """
    更新当前激活的标签页，并据此更新侧边栏和页面URL。

    参数:
    - to_active_tab: 要激活的标签页的标识符。
    - tab_list: 包含所有标签页信息的列表。

    返回值:
    - pathname: Dash的多页面模式下，需要对_pages_location对象的pathname和search属性进行更新，才能够激活URL跳转。
    - search: 更新后的查询参数。
    - sidebar_analysis_tab: 更新后的侧边栏内容。
    - tab_list: 更新后的标签页列表。
    """
    # 检查即将激活的标签是否与之前激活的标签相同，若相同则不进行任何更新
    if to_active_tab==global_var["pre_active_tab"]:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # 检查即将激活的标签是否已在标签列表中
    contains_active_tab = any(item['value'] == to_active_tab for item in tab_list)
    if contains_active_tab:
        # 如果标签已存在，不对标签列表进行更新
        tab_list = dash.no_update   
        # 判断即将激活的标签是否为特殊页面
        if to_active_tab in spec_pages:
            parsed_url = urlparse(spec_pages[to_active_tab])
            pathname = parsed_url.path
            search = parsed_url.query
            # 在特殊页面创建侧边栏
            sidebar_analysis_tab = market_stepper_placeholder
        else:
            # 非特殊页面的默认设置
            pathname = "/variety/basis"
            search = f"?variety_id={to_active_tab}"
            sidebar_analysis_tab = create_variety_stepper(to_active_tab)
    else:
        # 标签不存在于标签列表时的处理
        # 判断即将激活的标签是否为特殊页面
        if to_active_tab in spec_pages:
            parsed_url = urlparse(spec_pages[to_active_tab])
            pathname = parsed_url.path
            search = parsed_url.query
            # 在特殊页面创建侧边栏
            sidebar_analysis_tab = dash.no_update
        else:
            # 非特殊页面的默认设置
            pathname = "/variety/basis"
            search = f"?variety_id={to_active_tab}"
            sidebar_analysis_tab= create_variety_stepper(to_active_tab)
        
        # 通过DataWorks获取品种ID与名称的映射关系，并添加新标签到标签列表
        with DataWorks() as dws:
            variety_id_name_map, variety_name_id_map = dws.get_variety_map()
        tab_list.append({"value": to_active_tab, "label": variety_id_name_map[to_active_tab]})
    
    # 更新全局变量中之前激活的标签信息
    global_var["pre_active_tab"] = to_active_tab
    
    return pathname, search, sidebar_analysis_tab, tab_list

@app.callback(
    Output("page-switch-tabs", "data", allow_duplicate=True),
    Output("page-switch-tabs", "value", allow_duplicate=True),
    Input("button-remove-tab", "n_clicks"),
    State("page-switch-tabs", "value"),
    State("page-switch-tabs", "data"),
    prevent_initial_call=True,
)
def remove_tab(n_clicks, value, data):
    if len(data) <=1:
        return data, value
    select_index = [index for index, item in enumerate(data) if value not in item['value']]
    del data[select_index[0]]
    active_value = data[0]['value']
    return data, active_value

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)