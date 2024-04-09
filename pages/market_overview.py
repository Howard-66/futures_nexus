import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

main_content = html.Div('This is our Home page content.')

def layout():
    layout = html.Div([
        # dbc.Col(sidebar,),
        dbc.Col(main_content,)
    ])
    return layout