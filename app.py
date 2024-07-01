import pandas as pd
import dash
from dash import Dash, _dash_renderer, dcc, html, callback, Input, Output, State, clientside_callback, MATCH, ALL, ALLSMALLER
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dataworks import DataWorks
import re
from datetime import datetime
import global_env as ge

_dash_renderer._set_react_version("18.2.0")
CurrentUser = 'Howard'

main_menu = dmc.Group(
    [
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("市场全景", variant="subtle", className="primary_content", leftSection=DashIconify(icon="uiw:global", width=20))),               
            ],
        ),                             
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("金属", variant="subtle", className="primary_content", leftSection=DashIconify(icon="icon-park-outline:heavy-metal", width=24))),
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
                dmc.MenuTarget(dmc.Button("能源", variant="subtle", className="primary_content", leftSection=DashIconify(icon="material-symbols:energy-savings-leaf-outline", width=24))),
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
                dmc.MenuTarget(dmc.Button("化工", variant="subtle", className="primary_content", leftSection=DashIconify(icon="mdi:chemical-weapon", width=24))),
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
                dmc.MenuTarget(dmc.Button("农产品", variant="subtle", className="primary_content", leftSection=DashIconify(icon="ic:outline-agriculture", width=24))),
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
                dmc.MenuTarget(dmc.Button("自选", variant="subtle", className="primary_content", leftSection=DashIconify(icon="mdi:favorite-settings-outline", width=24))),               
            ],
        ),                       
        dmc.Menu(                    
            [
                dmc.MenuTarget(dmc.Button("设置", variant="subtle", className="primary_content", leftSection=DashIconify(icon="icon-park-outline:config", width=24))),
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
                        DashIconify(icon="simple-icons:bitcoincash", width=24, className="primary_content"),
                        dmc.Text("Futures Nexus", className="primary_content", size="xl"),
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
                        dmc.Select(searchable=True, clearable=True, id="variety-search", size="xs",
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
    p=5,
    withBorder=False,
    # style={"backgroundColor": "#f5f5f5"}
    className="panel_container",
)

# 创建一级NavLink的函数
def create_primary_nav_links():
    nav_links = []
    with DataWorks() as dws:
        variety_id_name_map, variety_name_id_map = dws.get_variety_map()
        user_json='setting/user.json'
        user_setting = dws.load_json_setting(user_json)
        for category, items in user_setting["Favorites"].items():
            icon = DashIconify(icon="fluent-mdl2:favorite-list", width=24)
            nav_links.append(
                dmc.NavLink(
                    label=category,
                    leftSection=icon,
                    childrenOffset=28,
                    children=[dmc.NavLink(label=variety_id_name_map[label], variant="subtle", href=f"/variety/basis?variety_id={label}") for label in items],
                    variant="subtle",
                    opened=True,
                    active=True,
                )
            )
    return nav_links

quick_access = html.Div(
    style={"width": ge.NavbarWidth, "height": "auto"},
    id="favorite-container",
    children=create_primary_nav_links()
)

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

note_cards = dmc.Stack(
    [
        dmc.Space(h=5),
        dmc.Group(
            [
                dmc.ActionIcon(
                    DashIconify(icon="carbon:new-tab", width=24),
                    size="sm",
                    radius="sm",
                    variant="subtle",
                    id="new-note-button",
                ),
                # dmc.ActionIcon(
                #     DashIconify(icon="carbon:list", width=24),
                #     size="sm",
                #     radius="sm",
                #     variant="subtle",
                # ),
                dmc.Switch(label="全部商品", id="show-all-varieties", checked=False, labelPosition="left", radius="lg", size='xs'),
            ],
            justify="space-around",
            gap="xs",
        ),
        dmc.Divider(size="sm"),
        dmc.ScrollArea(
            [],
            h=ge.MainContentHeight-ge.NoteEditHeight,
            scrollbarSize=5,
            type="hover",
            offsetScrollbars=True,
            id="note-list"
        ),
        dmc.Divider(size="sm", label="交易笔记", labelPosition="center"),
        dmc.Group(
            [
                dmc.DateInput(
                    id="note-date-input",
                    placeholder="日期",
                    size="xs",
                    radius="sm",
                    # value=datetime.now().date(),
                    valueFormat="YYYY-MM-DD",
                    variant="unstyle",
                    w=100,
                ),
                dmc.Select(
                    placeholder="类型",
                    data = [{"value": v, "label": v} for v in ["行情跟踪","进场关注", "加仓关注", "止盈/减仓", "止损/减仓", "过期关闭"]],
                    clearable=True,
                    size="xs",
                    radius="sm",
                    id="note-type-select",
                    w=100
                ),
            ],
            justify="flex-start",
            gap=2,
        ),

        dmc.Textarea(
            id="content-textarea",
            # label="多空分析",
            placeholder="多头:\n\n空头:\n\n交易计划:\n\n",
            autosize=True,
            minRows=6,
            maxRows=12,
            # variant="filled",
            radius="sm",
            size="sm",
        ),
        dmc.Group(
            [
                dmc.Button(
                    "删除",
                    id="remove-note-button",
                    variant="outline",
                    color="gray",
                    size="xs",
                ),
                dmc.Button(
                    "添加",
                    id="save-note-button",
                    variant="outline",
                    color="blue",
                    size="xs",
                ),
            ],
            justify="flex-end",            
        ),
    ],
    gap="xs",
    justify="center",
)

# 侧边栏-标签切换
sidebar_tabs =dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.TabsTab("分析", value="analysis"),
                dmc.TabsTab("笔记", value="chain"),
                dmc.TabsTab("自选", value="favorite"),
            ]
        ),
        dmc.TabsPanel([market_stepper_placeholder,variety_stepper_placeholder], value="analysis", p="md", id="sidebar-analysis-tab"),
        dmc.TabsPanel(note_cards, value="chain", id="sidebar-chain-tab"),
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
    color=ge.PrimaryLineColor,
    style={"backgroundColor": ge.MainContentBGColor}
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
        dmc.GridCol(dmc.Burger(id="burger-button", opened=True, size="xs", className="primary_content"), span="content"),
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
        dmc.Divider(variant="solid", size="sm"),                    
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
        dmc.AppShellHeader(header, withBorder=False, className="background_container"),
        dmc.AppShellNavbar(navbar, withBorder=True, className="panel_container"),
        dmc.AppShellAside("Aside", withBorder=True),
        dmc.AppShellMain(page_content, pt=ge.MainContentPaddingTop, className="background_container"),
        # dmc.AppShellFooter("Footer")
    ],
    header={"height": ge.HeaderHeight},
    padding="xl",
    navbar={
        "width": ge.NavbarWidth,
        "breakpoint": "md",
        "collapsed": {"desktop": False, "mobile": True},
        "opened": True,
    },
    aside={
        "width": ge.AsideWidth,
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
    "pre_active_tab": None,         # 上一个激活的tab
    "current_edit_note": None,      # 当前编辑的笔记
    "show_all_varieties": False,    # 是否显示所有品种的笔记
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
    if match:
        return match.group(1)
    return dash.no_update

def _create_note_card(date, variety_id, variety_name, type, content, like=0, dislike=0):
    date_dt = pd.to_datetime(date)
    date_str = date_dt.strftime("%Y-%m-%d")
    index_name = f"{variety_id}.{date_str}"
    like_color = ge.PrimaryLongColor if like==1 else ge.PrimaryNeutralColor
    dislike_color = ge.PrimaryShortColor if dislike==1 else ge.PrimaryNeutralColor
    card = dmc.Card(
        children=[
            dmc.Group(
                [
                    dmc.Text(variety_name, size="sm"),
                    dmc.Text(date_str, size="xs"),
                    dmc.Badge(type, size="sm", variant="light", className="primary_content"),
                ],
                justify="space-between",
                mb="xs",
                gap=0,
            ),
            dmc.Spoiler(
                showLabel="...",
                hideLabel="...",
                maxHeight=30,
                children=[dmc.Text(content, size="xs", c="dimmed")],
                className="spoiler_label"
            ),
            dmc.Group(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="iconoir:thumbs-up", width=20, color=like_color),
                        size="xs",
                        radius="sm",
                        variant="subtle",
                        id={"type": "like_note", "index": index_name}
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="iconoir:thumbs-down", width=20, color=dislike_color),
                        size="xs",
                        radius="sm",
                        variant="subtle",
                        id={"type": "dislike_note", "index": index_name}
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="ep:edit", width=20),
                        size="xs",
                        radius="sm",
                        variant="subtle",
                        id={"type": "edit_note", "index": index_name}
                    ),
                ],
                justify="flex-end",
                gap="xs"
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="sm",
        mb=5,
        p="xs",
    )
    return card

def _create_note_list(variety_id=None):
    with DataWorks() as dws:
        if variety_id:
            df_note_list = dws.get_data_by_symbol('notes', variety_id)
        else:
            df_note_list = dws.get_data('notes')
        variety_id_name_map, variety_name_id_map = dws.get_variety_map()        
    new_note_list = []
    for index, row in df_note_list.iterrows():
        variety_id = row['variety']
        variety_name = variety_id_name_map[variety_id]
        card = _create_note_card(row['date'], variety_id, variety_name, row['type'], row['content'], row['like'], row['dislike'])
        new_note_list.append(card)
    return new_note_list

@app.callback(
    Output("_pages_location", "pathname"),
    Output("_pages_location", "search"),
    Output("sidebar-analysis-tab", "children"),
    Output("page-switch-tabs", "data", allow_duplicate=True),
    Output("note-list", "children"),
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

    def _create_variety_stepper(variety_id):
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
    
    # 检查即将激活的标签是否与之前激活的标签相同，若相同则不进行任何更新
    if to_active_tab==global_var["pre_active_tab"]:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
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
            sidebar_analysis_tab = _create_variety_stepper(to_active_tab)
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
            sidebar_analysis_tab= _create_variety_stepper(to_active_tab)
        
        # 通过DataWorks获取品种ID与名称的映射关系，并添加新标签到标签列表
        with DataWorks() as dws:
            variety_id_name_map, variety_name_id_map = dws.get_variety_map()
        tab_list.append({"value": to_active_tab, "label": variety_id_name_map[to_active_tab]})
    
    # 更新全局变量中之前激活的标签信息
    global_var["pre_active_tab"] = to_active_tab
    show_all = global_var["show_all_varieties"]
    to_active_tab = None if show_all else to_active_tab
    note_list = _create_note_list(to_active_tab)
    
    return pathname, search, sidebar_analysis_tab, tab_list, note_list

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

@app.callback(
    Output("note-list", "children", allow_duplicate=True),
    Input("show-all-varieties", "checked"),
    State("_pages_location", "search"),
)
def show_all_varieties(show_all, search):
    if show_all:
        note_list = _create_note_list()
    else:
        match = re.search(r'variety_id=([A-Za-z]+)', search)
        variety_id = match.group(1) if match else None
        note_list = _create_note_list(variety_id)
    global_var["show_all_varieties"] = show_all
    return note_list

@app.callback(
    Output("note-date-input", "value"),
    Output("note-type-select", "value"),
    Output("content-textarea", "value"),
    Output("save-note-button", "children"),
    Output("remove-note-button", "children"),
    Input("new-note-button", "n_clicks")
)
def new_note(n_clicks):
    global_var["current_edit_note"] = None
    return datetime.now().date(), None, '', '添加', '重置'

@app.callback(
    Output("note-date-input", "value", allow_duplicate=True),
    Output("note-type-select", "value", allow_duplicate=True),
    Output("content-textarea", "value", allow_duplicate=True),
    Output("note-list", "children", allow_duplicate=True),
    Input("remove-note-button", "n_clicks"),
    State("remove-note-button", "children"),
)
def remove_or_reset_note(n_clicks, mode):
    if mode=='重置':
        return datetime.now().date(), None, '', dash.no_update
    elif mode=='删除':
        current_note = global_var["current_edit_note"]
        if current_note is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        variety_id, date = current_note
        with DataWorks() as dws:
            dws.delete_data('notes', f"variety='{variety_id}' AND date='{date}'")
            show_all = global_var["show_all_varieties"]
            variety_id = None if show_all else variety_id
            note_list = _create_note_list(variety_id)
        return datetime.now().date(), None, '', note_list

@app.callback(
    Output("note-list", "children", allow_duplicate=True),
    Output("save-note-button", "children", allow_duplicate=True),
    Input("save-note-button", "n_clicks"),
    State("note-date-input", "value"),
    State("note-type-select", "value"),
    State("content-textarea", "value"),
    State("save-note-button", "children"),
    State("_pages_location", "search"),
    State("note-list", "children"),
)
def save_note(n_clicks, date, type, content, mode, search, note_list):    
    if type is None or content is None:
        return dash.no_update, dash.no_update
    
    with DataWorks() as dws:
        if mode=='添加':
            match = re.search(r'variety_id=([A-Za-z]+)', search)
            if match:
                variety_id = match.group(1)
            else:
                return dash.no_update, dash.no_update
            variety_id_name_map, variety_name_id_map = dws.get_variety_map()
            variety_name = variety_id_name_map[variety_id]
            df = pd.DataFrame({
                'date': [date],
                'user': [CurrentUser],
                'variety': [variety_id],
                'type': [type],
                'content': [content],
                'like': 0,
                'dislike': 0
            })
            # df_note_list = dws.get_data_by_symbol('notes', variety_id)
            dws.save_data(df, 'notes', mode='append')
            new_card = _create_note_card(date, variety_id, variety_name, type, content)
            note_list.append(new_card)
            return note_list, '保存'
        elif mode=='保存':
            current_note = global_var["current_edit_note"]
            if current_note is None:
                return dash.no_update, dash.no_update
            variety_id, date = current_note
            note_dict = {
                'type': type,
                'content': content,
            }
            dws.update_data('notes', note_dict, f"variety='{variety_id}' AND date='{date}'")
            show_all = global_var["show_all_varieties"]
            variety_id = None if show_all else variety_id
            updated_note_list = _create_note_list(variety_id)
            return updated_note_list, dash.no_update
        else:
            return dash.no_update, dash.no_update

# 编辑按钮回调
@app.callback(
    Output("note-date-input", "value", allow_duplicate=True),
    Output("note-type-select", "value", allow_duplicate=True),
    Output("content-textarea", "value", allow_duplicate=True),
    Output("save-note-button", "children", allow_duplicate=True),
    Output("remove-note-button", "children", allow_duplicate=True),
    Input({"type": "edit_note", "index": ALL}, "n_clicks"),
    State({"type": "edit_note", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def edit_note(n_clicks, index):
    if all(element is None for element in n_clicks):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    else:
        triggered_id = ctx.triggered[0]['prop_id']
        # 正则表达式模式
        pattern = r'"index":"(.*?)"'
        # 使用正则表达式进行匹配
        match = re.search(pattern, triggered_id)
        # 提取匹配的内容
        if match:
            index_value = match.group(1)
            variety_id, date = index_value.split('.')
            global_var["current_edit_note"] = (variety_id, date)
            with DataWorks() as dws:
                df_note = dws.get_data('notes', f"variety='{variety_id}' AND date='{date}'")
            note = df_note.iloc[0]
            return note['date'], note['type'], note['content'], '保存', '删除'
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output({"type": "like_note", "index": MATCH}, "children"),
    Input({"type": "like_note", "index": MATCH}, "n_clicks"),
    State({"type": "like_note", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def like_note(n_clicks, id):
    if n_clicks is None:
        return dash.no_update
    variety_id, date = id['index'].split('.')
    with DataWorks() as dws:
        note = dws.get_data('notes', f"variety='{variety_id}' AND date='{date}'").iloc[0]
        like = False if note['like'] is None else note['like']
        like = not like
        dws.update_data('notes', {'like': like}, f"variety='{variety_id}' AND date='{date}'")
    icon_color = ge.PrimaryLongColor if like else ge.PrimaryNeutralColor
    icon = DashIconify(icon="iconoir:thumbs-up", width=20, color=icon_color)
    return icon

@app.callback(
    Output({"type": "dislike_note", "index": MATCH}, "children"),
    Input({"type": "dislike_note", "index": MATCH}, "n_clicks"),
    State({"type": "dislike_note", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def dislike_note(n_clicks, id):
    if n_clicks is None:
        return dash.no_update
    variety_id, date = id['index'].split('.')
    with DataWorks() as dws:
        note = dws.get_data('notes', f"variety='{variety_id}' AND date='{date}'").iloc[0]
        dislike = False if note['dislike'] is None else note['dislike']
        dislike = not dislike
        dws.update_data('notes', {'dislike': dislike}, f"variety='{variety_id}' AND date='{date}'")
    icon_color = ge.PrimaryShortColor if dislike else ge.PrimaryNeutralColor
    icon = DashIconify(icon="iconoir:thumbs-down", width=20, color=icon_color)
    return icon

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)