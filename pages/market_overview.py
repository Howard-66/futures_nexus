import dash
from dash import html
import components.sidebar as sidebar
from components.sidebar import get_sidebar
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "position": "fixed",
    "left": "12rem",
    "top": "3.5rem",
    "margin-left": "1rem",
    "margin-right": "1rem",
    "padding": "0rem 0rem",
}

main_content = html.Div('This is our Home page content.', style=CONTENT_STYLE),

layout = html.Div([
    
    dbc.Row(
        [
            dbc.Col(sidebar.layout,),
            dbc.Col(main_content,)
        ],
    )
])
