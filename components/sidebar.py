import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import components.style as style
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("产业链视图", active=True, href="#")),
        dbc.NavItem(dbc.NavLink("螺纹钢", href="#")),
        dbc.NavItem(dbc.NavLink("铁矿石", href="#")),
        dbc.NavItem(dbc.NavLink("焦炭", disabled=True, href="#")),
    ],
    vertical="md",
)

chain_variety_nav = dbc.Nav(
    children=[
    ],
    pills=True,
    vertical=True,
)

def get_sidebar(chain_id=None, id_name_map=None, chain_variety=None):
    if chain_id is None:
        chain_variety_nav.children=[]
    else:
        chain_variety_nav.children = [         
            dbc.NavLink("产业链视图", href=f"/chain/overview?chain_id={chain_id}", active="exact"),
        ]
        for variety in chain_variety:
            nav_link = dbc.NavLink(id_name_map[variety], href=f"/variety/basis?variety_id={variety}&chain_id={chain_id}", active="exact")
            chain_variety_nav.children.append(nav_link)
    card_content = [
        dbc.CardHeader("快速入口"),
        dbc.CardBody(
            [
                chain_variety_nav,
            ]
        ),
    ]
    layout = html.Div(
        [
            # dbc.Row(html.P('Search')),
            dbc.Row(dbc.Card(card_content, color="primary", outline=True), className="mb-4",),
        ],
        style=style.SIDEBAR_STYLE
    )
    return layout
