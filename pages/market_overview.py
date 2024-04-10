import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

main_content = html.Div('This is our Home page content.')

def layout():
    layout = html.Div([
        main_content,
    ])
    return layout