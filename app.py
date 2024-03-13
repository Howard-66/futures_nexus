import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

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
            in_navbar=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("动力煤产业链", href="/chain/coal"), 
                dbc.DropdownMenuItem("石油产业链", href="/chain/oil"),
                dbc.DropdownMenuItem("原油产业链", href="/chain/crude"),
             ],
            label="能源",
            nav=True,
            in_navbar=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("化工产业链", href="/chain/chemical"),
                dbc.DropdownMenuItem("沥青产业链", href="/chain/asphalt"),
                dbc.DropdownMenuItem("橡胶产业链", href="/chain/rubber"),
             ],
            label="化工",
            nav=True,
            in_navbar=True,
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
            in_navbar=True,
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
            in_navbar=True,
        ),                
    ],
    navbar=True,
    # horizontal='end'
)

# this example that adds a logo to the navbar brand
nav_bar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='assets/logo.png', height="30px")),
                        dbc.Col(dbc.NavbarBrand("Futures Nexus", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                # href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Input(type="search", placeholder="Search")
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Search", color="primary", className="ms-2"
                            ),
                            # set width of button column to auto to allow
                            # search box to take up remaining space.
                            width="auto",
                        ),
                    ],
                    # add a top margin to make things look nice when the navbar
                    # isn't expanded (mt-3) remove the margin on medium or
                    # larger screens (mt-md-0) when the navbar is expanded.
                    # keep button and search box on same row (flex-nowrap).
                    # align everything on the right with left margin (ms-auto).
                    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
                    align="center",
                ),
                id="navbar-collapse-search",
                navbar=True,
            ),            
            dbc.Collapse(
                dbc.Nav(
                    [
                        main_menu,
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse-mainmenu",
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

app.layout = html.Div([
    dbc.Row(nav_bar),
    # dbc.Row(
    #     html.Div([
    #         html.Div(
    #             dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #         ) for page in dash.page_registry.values()
    #     ]),
    # ),
    dbc.Row(dash.page_container),
])

if __name__ == '__main__':

    app.run(debug=True)
