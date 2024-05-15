# from numba import jit
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
from asteval import Interpreter
import re
from functools import reduce

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
        fig = go.Scatter(x=self.data['date'], y=self.data[self.name], name=self.name,
                            mode='lines',
                            fill=fill,
                            line=dict(color=color),
                            opacity=self.opacity,
                            showlegend=self.showlegend)
        # fig = px.line(self.data, x='date', y=self.name,
        #             title=self.name,
        #             line_shape='linear',  # 这是默认设置，可以指定为 'spline' 等
        #             render_mode='svg',  # 'svg' 或 'webgl'，webgl 更适合大数据集
        #             # labels={'date': 'Date', self.name: 'Value'},
        #             color_discrete_sequence=[color])  # 设定线条颜色
        # fig.update_traces(fill=fill, opacity=self.opacity, showlegend=self.showlegend)
        return fig

class RankColorIndicator(Indicator): 
    DEFAULT_WINDOW = 240
    OVER_BUY = 0.8
    OVER_SELL = 0.2
    LONG_COLOR = 'red'
    NO_COLOR = 'gray'
    SHORT_COLOR = 'green'

    # def calculate_pandas(self, **kwargs):
    #     if self.data is None:
    #         self.data = self.variety.get_data(self.name)
    #     direction = self.config.get('Direction', 'Long')
    #     roll_window = kwargs.get('window', self.DEFAULT_WINDOW)
    #     over_buy = kwargs.get('over_buy', self.OVER_BUY)
    #     over_sell = kwargs.get('over_sell', self.OVER_SELL)
    #     # color_map = self.params.get('color_map', [self.LONG_COLOR, self.NO_COLOR, self.SHORT_COLOR])
    #     # Pandas版本
    #     # self.data[self.name+'_rank'] = self.data[self.name].rolling(window=roll_window, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
    #     # Numpy版本（速度更快）
    #     np_data = self.data[self.name].to_numpy()
    #     self.data[self.name+'_rank'] = RRP(np_data, roll_window)
    #     if direction=='Long':
    #         self.data[self.name+'_color'] = [self.LONG_COLOR if x > over_buy else self.SHORT_COLOR if x < over_sell else self.NO_COLOR for x in self.data[self.name+'_rank']]
    #     else:
    #         self.data[self.name+'_color'] = [self.SHORT_COLOR if x > over_buy else self.LONG_COLOR if x < over_sell else self.NO_COLOR for x in self.data[self.name+'_rank']]
    #     return self.data

    def calculate(self, **kwargs):
        if self.data is None:
            self.data = self.variety.get_data(self.name)
        
        # 提取变量，避免多次访问字典
        config = self.config
        direction = config.get('Direction', 'Long')
        roll_window = kwargs.get('window', self.DEFAULT_WINDOW)
        over_buy = kwargs.get('over_buy', self.OVER_BUY)
        over_sell = kwargs.get('over_sell', self.OVER_SELL)
        
        # 使用 NumPy 进行滚动排名计算
        np_data = self.data[self.name].to_numpy()
        rank_data = RRP(np_data, roll_window)
        self.data[self.name+'_rank'] = rank_data
        
        # 提取颜色变量
        long_color = self.LONG_COLOR
        short_color = self.SHORT_COLOR
        no_color = self.NO_COLOR
        
        # 根据方向设置颜色，优化循环
        if direction == 'Long':
            color_array = np.where(rank_data > over_buy, long_color,
                                np.where(rank_data < over_sell, short_color, no_color))
        else:
            color_array = np.where(rank_data > over_buy, short_color,
                                np.where(rank_data < over_sell, long_color, no_color))
        
        # 将结果转换回 DataFrame
        self.data[self.name+'_color'] = color_array
        
        return self.data
    
    def figure(self, **kwargs):
        # 提取常用变量
        data = self.data
        name = self.name
        color = data[f'{name}_color']
        opacity = self.opacity
        showlegend = self.showlegend

        # 创建条形图
        fig = go.Bar(
            x=data['date'], 
            y=data[name], 
            name=name, 
            marker=dict(color=color, opacity=opacity),
            showlegend=showlegend,
        )
        # fig = go.Bar(x=self.data['date'], y=self.data[self.name], name=self.name, 
        #                     marker=dict(color=self.data[self.name+'_color'], opacity=self.opacity),
        #                     showlegend=self.showlegend,
        #                     # hovertemplate='%{y:.2%}',
        #                     )        
        # fig = px.bar(self.data, x='date', y=self.name,
        #             title=self.name,
        #             # labels={'date': 'Date', self.name: 'Value'},
        #             color=self.name+'_color',  # 指定颜色列
        #             opacity=self.opacity,  # 设置透明度
        #             hover_data={self.name: ':.2%'})  # 设置悬浮提示的数据格式
        # fig.update_traces(showlegend=self.showlegend, width=80000000)        
        return fig    
    
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
        fig = go.Bar(x=self.data['date'], y=self.data[self.name], name=self.name, 
                            marker=dict(color=self.data[self.name+'_color'], opacity=0.6),
                            showlegend=self.showlegend,
                            # hovertemplate='%{y:.2%}',
                           )        
        # fig = px.bar(self.data, x='date', y=self.name,
        #             title=self.name,
        #             # labels={'date': 'Date', self.name: 'Value'},
        #             color=self.name+'_color',  # 指定颜色列
        #             opacity=self.opacity,  # 设置透明度
        #             hover_data={self.name: ':.2%'})  # 设置悬浮提示的数据格式
        # fig.update_traces(showlegend=self.showlegend, width=80000000)        
        return fig

class CalculateRankColorIndicator(RankColorIndicator):
    def calculate(self, **kwargs):
        def extract_variables(format_str):
            """从格式字符串中提取变量名"""
            # 正则表达式模式，匹配中文字符、英文字符和下划线组成的变量名
            variable_pattern = r'[a-zA-Z_\u4e00-\u9fa5]+'
            variables = re.findall(variable_pattern, format_str)
            unique_variables = list(set(variables))
            return unique_variables
        formula = self.config.get('Formula', None)
        factor_list = extract_variables(formula)
        factor_data = []
        aeval = Interpreter()       
        for factor in factor_list:                                                
             data = self.variety.get_data(factor)
             factor_data.append(data)
        self.data = reduce(lambda left,right: pd.merge(left,right,on='date', how='outer'), factor_data)
        for factor in factor_list:                                                
            aeval.symtable[factor] = self.data[factor]
        self.data[self.name] = aeval.eval(formula)        
        self.data.dropna(subset=[self.name], inplace=True)
        super().calculate()
        return self.data