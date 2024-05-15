import modules.indicator as indicator
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 实现 IndicatorManager 类
class ChartManager:
    def __init__(self, variety):
        self.variety = variety
        self.indicators = {}
        self.main_list = []
        self.main_y2_list = []
        self.sub_list = []
        self.data_index = variety.symbol_setting['DataIndex']         
        self.main_figure = None   

    def load_indicators(self):
        for key, item in self.data_index.items():
            class_name = item.get('Class', None)            
            if class_name and hasattr(indicator, class_name):
                indicator_class = getattr(indicator, class_name)
                indicator_instance = indicator_class(key, self.variety, item)
                self.add_indicator(key, indicator_instance)        

    def add_indicator(self, name, indicator):
        self.indicators[name] = indicator
        if indicator.chart_type =='Sub':
            self.sub_list.append(name)
        elif indicator.chart_type=='Main':
            self.main_list.append(name)
        elif indicator.chart_type=='Main_Y2':
            self.main_y2_list.append(name)
        else:
            raise Exception('indicator type error')

    def get_indicator(self, name):
        return self.indicators[name]
    
    def calculate_indicators(self):
        for name, indicator in self.indicators.items():
            indicator.calculate()

    def plot(self):
        def _add_trace(names, secondary_y=False, row=1, calculate_range=True):
            if calculate_range:
                first_indicator_name = names[0]
                indicator_data = self.indicators[first_indicator_name].data
                filtered_data = indicator_data[(indicator_data['date'] >= self.start_date) & (indicator_data['date'] <= self.end_date)]
                min_y = filtered_data[first_indicator_name].min() * 0.99
                max_y = filtered_data[first_indicator_name].max() * 1.01
            else:
                min_y = max_y = None

            for name in names:
                figure = self.indicators[name].figure()
                self.main_figure.add_trace(figure, row=row, col=1, secondary_y=secondary_y)
            
            return min_y, max_y

        # 检查并创建主图
        if self.main_figure is None:
            self.main_figure = self._create_main_figure()

        # 更新主图第一个坐标轴
        min_y, max_y = _add_trace(self.main_list, calculate_range=True)
        self.main_figure.update_xaxes(linecolor='gray', tickfont=dict(color='gray'), row=1, col=1)
        self.main_figure.update_yaxes(range=[min_y, max_y], linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1, row=1, col=1)

        # 更新主图第二坐标轴
        min_y, max_y = _add_trace(self.main_y2_list, secondary_y=True, calculate_range=True)
        self.main_figure.update_yaxes(range=[min_y, max_y], row=1, col=1, secondary_y=True)

        # 设置副图
        for i, name in enumerate(self.sub_list, start=2):
            min_y, max_y = _add_trace([name], row=i, calculate_range=True)
            self.main_figure.update_xaxes(linecolor='gray', tickfont=dict(color='gray'), row=i, col=1)
            self.main_figure.update_yaxes(range=[min_y, max_y], linecolor='gray', tickfont=dict(color='gray'), zerolinecolor='LightGray', zerolinewidth=1, row=i, col=1)


    def _create_main_figure(self):
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)
        self.end_date = now.strftime('%Y-%m-%d')
        self.start_date = one_year_ago.strftime('%Y-%m-%d')

        rows = len(self.sub_list) + 1
        specs = [[{"secondary_y": True}] for _ in range(rows)]
        row_heights = [0.5] + [0.1] * (rows - 1) 
        subtitles = [''] + self.sub_list
        main_figure = make_subplots(rows=rows, cols=1, 
                                    specs=specs, row_heights=row_heights, subplot_titles=subtitles, 
                                    shared_xaxes=True, vertical_spacing=0.02)    
        return main_figure
    
    def update_figure(self):
        self.main_figure.update_xaxes(
            showgrid=False,
            zeroline=True,
            linecolor='gray',
            dtick="M1",  # 按月显示
            ticklabelmode="instant",   # instant  period
            tickformat="%m\n%Y",
            tickfont=dict(color='gray'),
            rangebreaks=[dict(values=self.variety.get_trade_breaks())],
            # rangeslider_visible = False, # 下方滑动条缩放
            range=[self.start_date, self.end_date],
        )
        self.main_figure.update_yaxes(
            showgrid=False,
        )
        self.main_figure.update_layout(
            autosize=True,
            # width=3000,
            height=1200,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='#f5f5f5',  
            paper_bgcolor='#f5f5f5',
            hovermode='x unified',
            modebar={},
            legend=dict(
                orientation='h',
                yanchor='top',
                y=1,
                xanchor='left',
                x=0,
                # bgcolor='#f5f5f5',
                # bordercolor='LightSteelBlue',
                # borderwidth=0
            ),
        )
        self.main_figure.update_annotations(dict(
            x=0,  # x=0 表示最左边
            xanchor='left',  # 锚点设置为左边
            xref="paper",  # 位置参考整个画布的宽度
            yref="paper",  # 位置参考整个画布的高度
            font=dict(size=12)  # 可选的字体大小设置
        ))            
        return