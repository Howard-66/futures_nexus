import dash
from dash import html

dash.register_page(__name__, path="/variety/cycle", title='Futures Nexus: 周期性分析')

layout = html.Div([
    html.H1('This is our Cycle page'),
    html.Div('This is our Cycle page content.'),
])