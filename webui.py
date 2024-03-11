import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import chain

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "16rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# web app logo
app_logo = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# 市场全景导航栏
market_overview_nav = dbc.Nav(
    [
        dbc.NavLink("基差综合屏", href="/overview/basis", active="exact"),
        dbc.NavLink("期限综合屏", href="/overview/period", active="exact"),
        dbc.NavLink("产业链综合屏", href="/overview/chains", active="exact"),
        dbc.NavLink("模型分析", href="/overview/models", active="exact"),
    ],
    vertical=True,
    pills=True,
)

# 侧边栏
side_bar = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(src=app_logo, height="30px"),width=2),
                dbc.Col(html.H4("Futures Nexus", className="display-10"),width='auto'),
            ],
        ),            
        # html.Hr(),
        html.P(
            "quantitative analysis", className="p3"
        ),
        html.Div(id='sidebar-nav')
    ],
    style=SIDEBAR_STYLE,
)

# 主菜单
main_menu = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("市场全景", active=True, href="/"), ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("钢铁产业链", href="/chain/black_metals/overview"), 
                dbc.DropdownMenuItem("贵金属产业链", href="/chain/precious_metals"),
                dbc.DropdownMenuItem("铝产业链", href="/chain/alum"),
                dbc.DropdownMenuItem("铜产业链", href="/chain/copper"),
             ],
            label="金属",
            nav=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("动力煤产业链", href="/chain/coal"), 
                dbc.DropdownMenuItem("石油产业链", href="/chain/oil"),
                dbc.DropdownMenuItem("原油产业链", href="/chain/crude"),
             ],
            label="能源",
            nav=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("化工产业链", href="/chain/chemical"),
                dbc.DropdownMenuItem("沥青产业链", href="/chain/asphalt"),
                dbc.DropdownMenuItem("橡胶产业链", href="/chain/rubber"),
             ],
            label="化工",
            nav=True,
        ),        
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("菜籽油产业链", href="/chain/rapeseed_oil"), 
                dbc.DropdownMenuItem("大豆产业链", href="/chain/soybeans"),
                dbc.DropdownMenuItem("糖产业链", href="/chain/sugar"),
                dbc.DropdownMenuItem("小麦产业链", href="/chain/wheat"),
                dbc.DropdownMenuItem("玉米产业链", href="/chain/corn"),
                dbc.DropdownMenuItem("棕榈油产业链", href="/chain/palm_oil"),
                dbc.DropdownMenuItem("生猪产业链", href="/chain/pig"),
             ],
            label="农产品",
            nav=True,
        ),
        dbc.NavItem(dbc.NavLink("自选", active=True, href="#"), ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("数据管理", href="/data_manage"),
                dbc.DropdownMenuItem("品种管理", href="/variety_manage"),
                dbc.DropdownMenuItem("设置", href="/setting"),
             ],
            label="我的",
            nav=True,
        ),                
    ],
    # navbar=True,
    # horizontal='end'
)

# 主内容页
main_content = html.Div(
    [
        dbc.Row(main_menu, align='start'),
        html.Hr(),
        dbc.Row(html.Div(id='main-content')),
    ],
    style=CONTENT_STYLE,
)

app.layout = html.Div([dcc.Location(id="url"), side_bar, main_content])

# chain.callback(app)

@app.callback(
        Output("sidebar-nav", "children"),
        Output("main-content", "children"),         
        [Input("url", "pathname")])
def render_page_content(pathname):
    side_bar_nav = None
    main_content = {}
    path_parts = pathname.strip('/').split('/')    
    module = path_parts[0]
    chain_name = path_parts[1] if len(path_parts) > 1 else None
    variety = path_parts[2] if len(path_parts) > 2 else None
    analysis_type = path_parts[3] if len(path_parts) > 3 else None

    home_page = html.Div("Home page!")
    not_found_page = html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

    if pathname == '/' or pathname =='':
        side_bar_nav = market_overview_nav
        main_content = home_page
    elif module == 'chain': 
        print(chain_name, variety, analysis_type)
        side_bar_nav, main_content = chain.page_router(chain_name, variety, analysis_type)
    else:
        main_content = not_found_page

    return side_bar_nav, main_content

if __name__ == "__main__":
    app.run_server(debug=True, port=8898)
