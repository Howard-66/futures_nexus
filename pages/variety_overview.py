import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/variety/overview")

# page_layout = html.Div([
#     html.H1('This is our Analytics page'),
#     html.Div([
#         "Select a city: ",
#         dcc.RadioItems(
#             options=['New York City', 'Montreal', 'San Francisco'],
#             value='Montreal',
#             id='analytics-input'
#         )
#     ]),
#     html.Br(),
#     html.Div(id='analytics-output'),
# ])

def layout(variety_id=None, **other_unknown_query_strings):
    return html.Div([
        html.H1(f'This is our {variety_id} Analytics page'),
        html.Div([
            "Select a city: ",
            dcc.RadioItems(
                options=['New York City', 'Montreal', 'San Francisco'],
                value='Montreal',
                id='analytics-input'
            )
        ]),
        html.Br(),
        html.Div(id='analytics-output'),
    ])

@callback(
    Output('analytics-output', 'children'),
    Input('analytics-input', 'value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'