import dash
from dash import html
import dash_mantine_components as dmc
import dash
from dash import html, dcc, callback, Input, Output, State
import dataworks as dw
import plotly.express as px

dash.register_page(__name__, path='/', title='Futures Nexus: 市场全景')

main_content = html.Div('This is our Home page content.')

heat_map_switch = dmc.ChipGroup(
    [dmc.Chip(x, value=x) for x in ["持仓量", "成交量"]],
    value="持仓量",
    id='heat-map-switch'
)

heat_map_panel = dmc.Paper(
    dmc.Stack(
        [
            dmc.Group([
                dmc.Text("市场热力图", size="lg"),
                heat_map_switch,
            ]),            
            dmc.LoadingOverlay(dcc.Graph(id='market-heatmap-placeholder', config={'displayModeBar': False}),),
        ]
    ),
    shadow="sm",
    radius="xs",
    p="xs",
    withBorder=True,         
)

class MarketOverviewPage:
    def __init__(self) -> None:
        self.main_content = None
        self.heatmap_data = None

    def get_layout(self):
        if self.main_content is None:
            layout = heat_map_panel
        else:
            layout = self.main_content
        return layout
    
    def create_heat_map(self, type):
        if self.heatmap_data is None:
            with dw.DataWorks() as dws:
                last_date = dws.get_last_date('dominant')
                sql = f"SELECT d.*, s.name, s.chain FROM dominant AS d INNER JOIN symbols AS s ON d.variety = s.code WHERE d.date = '{last_date}'"
                self.heatmap_data = dws.get_data_by_sql(sql)

        fig = px.treemap(self.heatmap_data, path=[px.Constant("市场热力图"), 'chain', 'name'], values=type,
                        color=type, 
                        color_continuous_scale='PuOr',  # PuOr/BrBG/Blues/Spectral_r
                        color_continuous_midpoint=self.heatmap_data[type].min())
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))    
        return fig

OverviewPages = {}

def layout():
    if 'MarketOverview' not in OverviewPages:
        market_overview = MarketOverviewPage()
        OverviewPages['MarketOverview'] = market_overview
        
    return OverviewPages['MarketOverview'].get_layout()

@callback(
    Output('market-heatmap-placeholder', 'figure'),
    Input('heat-map-switch', 'value'),
    allow_duplicate=True
)
def update_heat_map(type):
    if type is None:
        return dash.no_update
    return OverviewPages['MarketOverview'].create_heat_map(type)


@callback(
    Output('output', 'children', allow_duplicate=True),
    Input('market-heatmap-placeholder', 'clickData'),
    prevent_initial_call=True
)
def heatmap_callback(click_data):
    if click_data is None:
        return dash.no_update
    clicked_path = click_data['points'][0]['id']
    print(clicked_path)

@callback(
    Output('output', 'children', allow_duplicate=True),
    Input('open-variety-page', 'n_clicks'),
    State('market-heatmap-placeholder', 'clickData'),
    prevent_initial_call=True
)
def open_variety_page(n_clicks, heatmap_data):
    if heatmap_data is None:
        return dash.no_update
    clicked_path = heatmap_data['points'][0]['id']
    path_level = clicked_path.split('/')
    levels = len(path_level)
    chain_name = path_level[1] if levels>1 else None
    vareity_name = path_level[2] if levels>2 else None
    print(chain_name, vareity_name)