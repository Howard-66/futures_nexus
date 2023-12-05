# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import commodity

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dmc.Container([
    dmc.Title('商品基本面分析', color="blue", size="h3"),
    dmc.RadioGroup(
            [dmc.Radio(i, value=i) for i in  ['pop', 'lifeExp', 'gdpPercap']],
            id='my-dmc-radio-item',
            value='lifeExp',
            size="sm"
        ),
    dmc.Grid([
        # dmc.Col([
        #     dash_table.DataTable(data=df.to_dict('records'), page_size=12, style_table={'overflowX': 'auto'})
        # ], span=6),
        dmc.Col([
            dcc.Graph(figure={}, id='graph-placeholder')
        ], span=12),
    ]),

], fluid=True)

# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)
def update_graph(col_chosen):
    # fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    symbol_id = 'RB'
    symbol_name = '螺纹钢'
    fBasePath = 'steel/data/mid-stream/螺纹钢/'
    json_file = './steel/setting.json'
    symbol = commodity.SymbolData(symbol_id, symbol_name, json_file)
    merged_data = symbol.merge_data()
    symbol.symbol_data['基差'] = 0-symbol.symbol_data['基差']
    symbol.symbol_data['基差率'] = 0-symbol.symbol_data['基差率']
    df_figure = pd.DataFrame()
    df_figure['基差率颜色'] = symbol.symbol_data['基差率'] > 0
    df_figure['基差率颜色'] = df_figure['基差率颜色'].replace({True:1, False:0})

    max_y = symbol.symbol_data['主力合约收盘价'] .max() * 1.05
    min_y = symbol.symbol_data['主力合约收盘价'] .min() * 0.95

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]],
                    vertical_spacing=0.01, subplot_titles=('基差分析', '基差率', '库存'), 
                    row_width=[0.15, 0.15, 0.7])

    #fig_main = make_subplots(specs=[[{"secondary_y": True}]])
    fig_future_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['主力合约收盘价'], name='期货价格', marker_color='rgb(84,134,240)')
    fig_spot_price = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgb(105,206,159)')
    fig_basis = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', marker_color='rgb(239,181,59)')
    #fig_main.add_trace(fig_future_price)
    #fig_main.add_trace(fig_basis_rate, secondary_y=True)

    fig.add_trace(fig_basis, secondary_y=True)
    fig.add_trace(fig_future_price, row = 1, col = 1)
    fig.add_trace(fig_spot_price, row = 1, col = 1)

    fig_basis_rate = go.Bar(x=symbol.symbol_data['日期'], y = symbol.symbol_data['基差率'], name='基差率', marker_color='rgb(244,128,68)')
    #fig_basis_rate = go.Bar()
    #fig_basis_rate.mode = 'markers'
    # fig_basis_rate.x = df_rb0['日期']
    # fig_basis_rate.y = df_rb0['基差率']
    fig_basis_rate.marker.colorscale = ['green', 'red']
    fig_basis_rate.marker.color = df_figure['基差率颜色']
    #fig_basis_rate.marker.size = 2
    fig_basis_rate.marker.showscale = False
    fig_basis_rate.showlegend = False

    fig.add_trace(fig_basis_rate, row = 2, col = 1)
    fig_receipt = go.Scatter(x=symbol.symbol_data['日期'], y=symbol.symbol_data['仓单'], name='仓单', marker_color='rgb(239,181,59)')
    fig_storage = go.Bar(x=symbol.symbol_data['日期'], y=symbol.symbol_data['库存'], name='库存', marker_color='rgb(234,69,70)')
    #fig_storage = px.bar(df_rb0, x='日期', y='库存')
    fig.add_trace(fig_receipt, row = 3, col = 1, secondary_y=True)
    fig.add_trace(fig_storage, row = 3, col = 1)

    # trade_date = ak.tool_trade_date_hist_sina()['trade_date']
    # trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
    # dt_all = pd.date_range(start=symbol.symbol_data['日期'].iloc[0],end=symbol.symbol_data['日期'].iloc[-1])
    # dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    # dt_breaks = list(set(dt_all) - set(trade_date))

    # X轴坐标按照年-月显示
    fig.update_xaxes(
        showgrid=True,
        zeroline=True,
        dtick="M1",  # 按月显示
        ticklabelmode="period",   # instant  period
        tickformat="%b\n%Y",
        # rangebreaks=[dict(values=dt_breaks)],
        rangeslider_visible = False, # 下方滑动条缩放
        rangeselector = dict(
            # 增加固定范围选择
            buttons = list([
                dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
                dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
                dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
                dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
                dict(step = 'all')
                ]))
    )
    #fig.update_traces(xbins_size="M1")
    fig.update_layout(
        yaxis_range=[min_y,max_y],
        #autosize=False,
        #width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

# Run the App
if __name__ == '__main__':
    app.run(debug=True)