import dash
from dash import html

dash.register_page(__name__)

layout = html.H1("404: Page not found!")