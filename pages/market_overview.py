import dash
from dash import html
import components.style as style
from components.sidebar import get_sidebar
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

main_content = html.Div('This is our Home page content.', style=style.CONTENT_STYLE),

def layout():
    sidebar = get_sidebar()
    layout = html.Div([
        dbc.Row(
            [
                dbc.Col(sidebar,),
                dbc.Col(main_content,)
            ],
        )
    ])
    return layout