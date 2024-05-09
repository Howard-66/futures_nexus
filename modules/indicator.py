import pandas as pd


# 实现 Indicator 类
class Indicator:
    def __init__(self, name, func, params):
        self.name = name
        self.func = func
        self.params = params

    def calculate(self, data):
        return self.func(data, **self.params)

# 实现 IndicatorManager 类
class IndicatorManager:
    def __init__(self, data_source_manager):
        self.indicators = {}
        self.data_source_manager = data_source_manager

    def add_indicator(self, data_source_name, name, func, params):
        data = self.data_source_manager.get_data(data_source_name)
        self.indicators[name] = Indicator(name, func, params, data)

    def calculate_indicators(self):
        results = {}
        for name, indicator in self.indicators.items():
            results[name] = indicator.calculate(indicator.data)
        return results

# 实现 ChartConfig 类
import plotly.graph_objects as go

class ChartConfig:
    def __init__(self, indicator_results):
        self.indicator_results = indicator_results
        self.fig = go.Figure()

    def add_trace(self, data, trace_type="scatter", name="Trace", yaxis='y1', **kwargs):
        trace = getattr(go, trace_type)(x=data.index, y=data, name=name, yaxis=yaxis, **kwargs)
        self.fig.add_trace(trace)

    def set_layout(self, title, xaxis_title, yaxis_title, yaxis2_title=None, **layout_kwargs):
        layout = {
            'title': title,
            'xaxis_title': xaxis_title,
            'yaxis_title': yaxis_title,
            'yaxis': {'title': yaxis_title},
            'template': 'plotly_dark'
        }
        if yaxis2_title:
            layout['yaxis2'] = {'title': yaxis2_title, 'overlaying': 'y', 'side': 'right'}
        self.fig.update_layout(**layout, **layout_kwargs)

    def show(self):
        self.fig.show()

