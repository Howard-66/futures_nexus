# from numba import jit
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod

# @jit(nopython=True)
def RRP(data, window_size):
    """
    Rolling Rank Percentile-计算制定窗口周期内的百分位排名
    """
    # 结果数组
    rank_pct = np.full(data.shape, np.nan)  # 初始全为 NaN
    # 对于每个可能的窗口位置
    for i in range(window_size - 1, len(data)):
        window = data[i - window_size + 1:i + 1]
        sorted_indices = np.argsort(window)
        current_rank = 1+ np.where(sorted_indices == window_size - 1)[0][0]
        rank_pct[i] = current_rank / window_size  # 计算百分比排名

    return rank_pct

class Indicator(ABC):
    def __init__(self, name, variety, config, **params):
        self.name = name
        self.variety = variety
        self.config = config
        self.chart_type = config.get('Chart', 'None')
        self.order = config.get('Order', -1)
        self.opacity = config.get('Opacity', 0.5)
        self.showlegend = config.get('ShowLegend', False)
        self.params = params
        self.data = None

    @abstractmethod
    def calculate(self, **kwargs):
        """
        Abstract method to calculate the indicator values, to be implemented by subclasses.
        """
        pass

    @abstractmethod
    def figure(self, **kwargs):
        """
        Abstract method to calculate the indicator values, to be implemented by subclasses.
        """
        pass

### SimpleIndicator Class
class SimpleIndicator(Indicator): 
    LINE_COLOR = 'lightblue'
    def calculate(self, **kwargs):
        self.data = self.variety.get_data(self.name)
        return
    
    def figure(self, **kwargs):
        color = self.config.get('Color', self.LINE_COLOR)
        fill = self.config.get('Fill', 'none')
        fill = 'tozeroy' if fill=='Area' else fill
        # fig = go.Scatter(x=self.data['date'], y=self.data[self.name], name=self.name,
        #                     mode='lines',
        #                     fill=fill,
        #                     line=dict(color=color),
        #                     opacity=self.opacity,
        #                     showlegend=self.showlegend)
        fig = px.line(self.data, x='date', y=self.name,
                    title=self.name,
                    line_shape='linear',  # 这是默认设置，可以指定为 'spline' 等
                    render_mode='svg',  # 'svg' 或 'webgl'，webgl 更适合大数据集
                    labels={'date': 'Date', self.name: 'Value'},
                    color_discrete_sequence=[color])  # 设定线条颜色
        fig.update_traces(fill=fill, opacity=self.opacity, showlegend=self.showlegend)
        return fig

class RankColorIndicator(Indicator): 
    DEFAULT_WINDOW = 240
    OVER_BUY = 0.8
    OVER_SELL = 0.2
    LONG_COLOR = 'red'
    NO_COLOR = 'grey'
    SHORT_COLOR = 'green'

    def calculate(self, **kwargs):
        if self.data is None:
            self.data = self.variety.get_data(self.name)
        direction = self.config.get('Direction', 'Long')
        roll_window = kwargs.get('window', self.DEFAULT_WINDOW)
        over_buy = kwargs.get('over_buy', self.OVER_BUY)
        over_sell = kwargs.get('over_sell', self.OVER_SELL)
        # color_map = self.params.get('color_map', [self.LONG_COLOR, self.NO_COLOR, self.SHORT_COLOR])
        # Pandas版本
        # self.data[self.name+'_rank'] = self.data[self.name].rolling(window=roll_window, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
        # Numpy版本（速度更快）
        np_data = self.data[self.name].to_numpy()
        self.data[self.name+'_rank'] = RRP(np_data, roll_window)
        if direction=='Long':
            self.data[self.name+'_color'] = [self.SHORT_COLOR if x > over_buy else self.LONG_COLOR if x < over_sell else self.NO_COLOR for x in self.data[self.name+'_rank']]
        else:
            self.data[self.name+'_color'] = [self.LONG_COLOR if x > over_buy else self.SHORT_COLOR if x < over_sell else self.NO_COLOR for x in self.data[self.name+'_rank']]
        return self.data
    
    def figure(self, **kwargs):
        # fig = go.Bar(x=self.data['date'], y=self.data[self.name], name=self.name, 
        #                     marker=dict(color=self.data[self.name+'_color'], opacity=self.opacity),
        #                     showlegend=self.showlegend,
        #                     # hovertemplate='%{y:.2%}',
        #                     )        
        fig = px.bar(self.data, x='date', y=self.name,
                    title=self.name,
                    labels={'date': 'Date', self.name: 'Value'},
                    color=self.name+'_color',  # 指定颜色列
                    opacity=self.opacity,  # 设置透明度
                    hover_data={self.name: ':.2%'})  # 设置悬浮提示的数据格式
        fig.update_traces(showlegend=self.showlegend, width=86400000)        
        return fig    
    
class BasisRateRankColorIndicator(RankColorIndicator):
    def calculate(self, **kwargs):
        settle_price = self.variety.get_data('结算价')
        spot_price = self.variety.get_data('现货价格')
        self.data = pd.merge(settle_price, spot_price, on='date', how='outer') 
        self.data[self.name] = (self.data['现货价格'] - self.data['结算价']) / self.data['现货价格']
        super().calculate()
        return self.data
    
class MapColorIndicator(Indicator):
    COLOR_MAPPING = {
            'Short': {-1: 'red', -0.5:'gray', 0:'gray', 0.5:'gray', 1:'green'},
            'Long': {-1: 'green', -0.5:'gray', 0:'gray', 0.5:'gray', 1:'red'},
        }
    def calculate(self, **kwargs):
        self.data = self.variety.get_data(self.name)
        direction = self.config.get('Direction', 'Long')
        color_mapping = self.COLOR_MAPPING[direction]
        self.data[self.name+'_color'] = self.data[self.name].map(color_mapping)
        return self.data
    
    def figure(self, **kwargs):
        # fig = go.Bar(x=self.data['date'], y=self.data[self.name], name=self.name, 
        #                     marker=dict(color=self.data[self.name+'_color'], opacity=0.6),
        #                     showlegend=self.showlegend,
        #                     # hovertemplate='%{y:.2%}',
        #                    )        
        fig = px.bar(self.data, x='date', y=self.name,
                    title=self.name,
                    labels={'date': 'Date', self.name: 'Value'},
                    color=self.name+'_color',  # 指定颜色列
                    opacity=self.opacity,  # 设置透明度
                    hover_data={self.name: ':.2%'})  # 设置悬浮提示的数据格式
        fig.update_traces(showlegend=self.showlegend, width=86400000)        
        return fig

class ProfitRankColorIndicator(RankColorIndicator):
    def calculate(self, **kwargs):
        # TODO：实现利润计算指标
        pass