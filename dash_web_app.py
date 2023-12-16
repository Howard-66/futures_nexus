import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import dcc, Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={"width": "18rem", "position": "fixed", "height": "100%", "padding": "2rem 1rem", "background-color": "#f8f9fa"},
    id="sidebar"
)

content = html.Div(id="page-content", style={"margin-left": "18rem"})

toggle_button = html.Button("Toggle Sidebar", id="toggle")

app.layout = html.Div([dcc.Location(id="url"), toggle_button, sidebar, content])

@app.callback(
    Output("sidebar", "style"),
    Input("toggle", "n_clicks"),
    State("sidebar", "style"),
)
def toggle_sidebar(n, style):
    if n:
        if style["display"] == "block":
            style["display"] = "none"
        else:
            style["display"] = "block"
    return style

@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 3)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False
    return [pathname == f"/page-{i}" for i in range(1, 3)]

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.H1("Page 1")
    elif pathname == "/page-2":
        return html.H1("Page 2")
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__ == "__main__":
    app.run_server(port=8888)