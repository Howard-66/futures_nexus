import dash
from dash import html
from components.sidebar import get_sidebar
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

main_content = html.Div('This is our Home page content.'),

layout = html.Div([
    
    dbc.Row(
        [
            dbc.Col(get_sidebar(), width=1),
            dbc.Col(main_content, width='auto')
        ],
    )
])