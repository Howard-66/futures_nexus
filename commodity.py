import json
import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta,MO
import akshare as ak
from functools import reduce
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dataworks as dw

class SymbolChain:
    def __init__(self, id, name, config_file):
        self.id = id
        self.name = name
        self.config_file = config_file
        self.symbol_dict = {}

    def add_symbol(self, symbol):
        self.symbol_dict[symbol.name] = symbol

    def remove_symbol(self, symbol_name):
        self.symbol_dict.pop(symbol_name, None)

    def get_symbol(self, symbol_name):
        if symbol_name in self.symbol_dict:
            return self.symbol_dict[symbol_name]
        else:
            return None
        
    def initialize_data(self, dws):
        for _, symbol in self.symbol_dict.items():
            df = symbol.merge_data(dws)
        
class SymbolData:
    """品种数据类:
        用于品种对应的数据更新、加载、预处理和访问
    """
    
    def __init__(self, id, name, json_file, symbol_setting=''):
        """
        SymbolData类的构造函数,
    
        Args:
            id (str): 品种ID,商品期货为英文简写,例如:螺纹钢为'RB',
            name (str): 品种中文名称,例如:螺纹钢,
            json_file (str): 品种对应的json文件,主要存储品种的数据索引内容,使用工作目录的相对路径,同一个产业链使用统一的配置文件,
            symbol_setting (str, optional): 符号设置的字典,默认为空,
    
        Returns:
            SymbolData: 返回SymbolData对象,如果未提供id、name和配置文件,则返回空
        """
        if id =='' or name=='' or json_file == '':
            return None
        self.id = id # 商品ID（英文缩写）
        self.name = name # 商品名
        self.config_file = json_file # 品种配置文件（同一产业链使用相同的配置文件）
        self.basis_color = pd.DataFrame() # 基差率绘图颜色
        self.data_rank = pd.DataFrame() # 指标评级
        self.spot_months = pd.DataFrame() # 现货交易月
        self.signals = pd.DataFrame() # 指标信号
        if symbol_setting == '':
            with open(json_file, encoding='utf-8') as config_file:
                self.symbol_setting = json.load(config_file)[self.name]            
        else:
            self.config_symbol_setting(symbol_setting)

    def config_symbol_setting(self, symbol_setting):
        """
        更新配置文件的内容,    
        Args:
            symbol_setting (dict): 符号设置的字典,
    
        Raises:
            IOError: 如果读取或写入配置文件时发生错误,则抛出IOError异常,
        """
        # 方法实现代码...
        # 先读取已有配置文件内容
        try:
            with open(self.config_file, 'r', encoding='utf-8') as config_file:
                existing_data = json.load(config_file)
        except IOError as e:
            print(f"Error reading configuration: {e}")
            existing_data = {}

        # 将新内容添加到原有内容中
        if self.name not in existing_data:
            existing_data[self.name] = symbol_setting
        else:
            existing_data[self.name].update(symbol_setting)
        # existing_data.update({symbol_name: symbol_setting})
        self.symbol_setting = existing_data[self.name]

        # 将合并后的内容写入文件
        try:
            with open(self.config_file, 'w', encoding='utf-8') as config_file:
                json.dump(existing_data, config_file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving configuration: {e}")

    def load_choice_file(self, file_path):
        """读取choice数据终端导出的数据文件.
            Choiced导出文件格式对应的处理规则. 
            - 原文件第一行为“宏观数据“或类似内容,但read_excel方法未加载该行内容
            - 数据的第一行作为指标标题
            - 第一列作为日期
            - 前四行和最后一行都不是数据内容
            - 剔除“日期”字段为空的行和其他非数据内容（标识数据来源的文字内容）
            
            Choice文件导出注意事项:
            - 导出字段选择:指标名称、频率、单位、来源
            - 日期排序:降序
            - 图形设置:不导出图形
            - 勾选“使用函数方式导出”
        Args:
            file_path (str): Choice导出文件(.xlsx)的绝对路径

        Returns:
            dataframe: 将Choice导出文件内容加载到dataframe,并返回
        """
        if file_path=='':
            return None
        df = pd.read_excel(file_path)
        df.columns = df.iloc[0]
        df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        df = df[4:]
        df.reset_index(drop=True, inplace=True)
        df.dropna(axis=0, subset=['date'], inplace=True)
        df = df[df['date'] != '数据来源：东方财富Choice数据']
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_akshare_file(self, file_path):
        """读取通过AK Share接口下载保存的数据文件

        Args:
            file_path (str): 通过AKShare接口下载并保存的Excel文件绝对路径+文件名

        Returns:
            dataframe: 将加载的Excel文件经过格式化处理后以dataframe返回
        """
        if file_path == '':
            return None
        df = pd.read_excel(file_path)
        # 格式化日期
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        # 纠正AKShare基差/基差率计算错误（正负号）
        df['near_basis'] = -df['near_basis']
        df['dom_basis'] = -df['dom_basis']
        df['near_basis_rate'] = -df['near_basis_rate']
        df['dom_basis_rate'] = -df['dom_basis_rate']
        # df.rename(columns={'日期': 'date'}, inplace=True)
        # TODO:其他数据格式化
        return df

    def update_akshare_file(self, mode='append', start_date='', end_date=''):
        """通过AKShare接口更新历史数据

        Args:
            mode (str, optional): 更新模式. 默认值为 'append'.
            - initial: 根据指定的时间段初始创建数据文件,后续使用period模式向前补充、append模式向后补充
            - append: 根据文件最后记录,更新到当前日期,会覆盖更新历史数据中的最后一条记录
            - period: 仅更新指定时间段的数据（目前仅支持向前追加,不做去重）
            - all: 全部更新,并覆盖原数据\n
            start_date (str, optional): 数据更新的起始日期\n
            end_date (str, optional): 数据更新的默认日期.

        Returns:
            dataframe: 将新增数据与原数据合并并返回,同时保存至文件
        """
        basis_file = self.symbol_setting['DataIndex']['现货价格']['Path']
        if mode == 'append':
            df_basis = pd.read_excel(basis_file)
            df_basis.reset_index(drop=True, inplace=True)
            today = datetime.now().strftime("%Y%m%d")
            last_date = str(df_basis.iloc[-1]['date'])
            df_append = ak.futures_spot_price_daily(start_day=last_date, end_day=today, vars_list=[self.id])
            # 移除最后一条重复数据,用最新数据替代
            df_basis.drop(df_basis.shape[0]-1, inplace=True)
            df_basis =pd.concat([df_basis, df_append])
            df_basis.to_excel(basis_file, index=False)
            return df_basis
        elif mode=='period':
            if start_date=='' or end_date=='':
                return None
            df_basis = pd.read_excel(basis_file)
            df_basis.reset_index(drop=True, inplace=True)          
            try:
                df_period = ak.futures_spot_price_daily(start_day=start_date, end_day=end_date, vars_list=[self.id])
                df_basis =pd.concat([df_period, df_basis])
                # TODO: #目前仅支持向前补充数据,待增加与已有数据重叠更新（数据去重）
                df_basis.to_excel(basis_file, index=False)
                return df_basis                                
            except Exception as e:
                print(f"Error in downloading data: {e}") 
                return df_basis
        elif mode=='initial':
            if start_date=='' or end_date=='':
                return None
            try:
                df_basis = ak.futures_spot_price_daily(start_day=start_date, end_day=end_date, vars_list=[self.id])
                df_basis.to_excel(basis_file, index=False)
                return df_basis
            except Exception as e:
                print(f"Error in downloading data: {e}") 
                return df_basis
        else:
            # TODO: 待增加全部更新并覆盖已有数据功能
            # 获取当前日期  
            now = datetime.now()  
            # 获取前一个工作日  
            previous_workday = datetime.now() - relativedelta(days=1, weekday=MO)  
            # 统一设置所有数据起始日期为2011年1月4日
            start_date = "20110104"
            end_date = previous_workday.strftime("%Y%m%d")  
            print('other modes is not implemented in update_akshare_file.')
            return None

    def merge_data(self, dws):
        """对数据索引中引用到的数据进行合并
            根据数据源（Choice/AKShare）调用对应的文件加载方法,并按照约定格式化数据,日期数据格式化为datatime,并按照升序排列,对应日期确实数据的置位NaN,
        Returns:
            dataframe: 返回合并后的数据
        """
        column_dict= {}
        data_frames = []
        data_index = self.symbol_setting['DataIndex']
        for key in data_index:
            value_items =data_index[key]
            df_name = value_items['DataFrame']
            if df_name in locals():
                pass
            else:
                data_source = value_items['Source']
                if data_source=='Choice':
                    locals()[df_name] = self.load_choice_file(value_items['Path'])
                elif data_source=='SQLite':
                    locals()[df_name] = dws.get_data_by_symbol(value_items['Path'], '*', self.id)
                    locals()[df_name]['date'] = pd.to_datetime(locals()[df_name]['date'])
                elif data_source=='AKShare':
                    locals()[df_name] = self.load_akshare_file(value_items['Path'])
                else:
                    pass
                column_dict[df_name] = ['date']
            column_dict[df_name].append(value_items['Field'])
        for df_key in column_dict:
            locals()[df_key] = locals()[df_key][column_dict[df_key]]
            data_frames.append(locals()[df_key])
        self.symbol_data = reduce(lambda left,right: pd.merge(left,right,on='date', how='outer'), data_frames)
        for key in data_index:
            self.symbol_data.rename(columns={data_index[key]['Field']:key}, inplace=True)
        self.symbol_data.sort_values(by='date', ascending=True, inplace=True)
        # self.symbol_data['库存'] = self.symbol_data['库存'].fillna(method='ffill', limit=None)
        self.symbol_data['库存'] = self.symbol_data['库存'].ffill()
        if '基差' not in data_index:
            self.symbol_data['基差'] = self.symbol_data['现货价格'] - self.symbol_data['主力合约结算价']
            self.symbol_data['基差率'] = self.symbol_data['基差'] / self.symbol_data['现货价格']
        return self.symbol_data
    
    def history_time_ratio(self, field, df_rank=None, mode='time', trace_back_months='all', quantiles=[0, 20, 40, 60, 80, 100], ranks=[1, 2, 3, 4, 5]):
        """返回指定数据序列的历史分位
            计算数据在序列中的历史数值百分位或时间百分位,并根据区间划定分位.
        Args:
            - field (str): symbol_data中的字段名称
            - df_rank (DataFrame, optional): 指定用于存储返回结果的DataFrame. 默认为空:创建DataFrame并返回；不为空时直接追加“历史百分位”、“历史分位”两列结果.
            - mode (str, optional): 计算模式. 'time':默认值,计算数据在序列中的时间百分位；'value':根据数据在序列中的最大值最小值范围,确定百分位.
            - trace_back_months (str/int, optional): 计算历史百分位时使用的历史数据范围,默认为all,即使用全部历史数据；为整数时,指定向前追溯使用的月份数量. 
            - quantiles (list, optional): 分位分区. 默认分区为 [0, 20, 40, 60, 80, 100].
            - ranks (list, optional): 分区标签. 默认为 [1, 2, 3, 4, 5].

        Returns:
            DataFrame: df_rank为空时,创建并返回一个新的DataFrame,包含“历史百分位”、“历史分位”两列结果；不为空时在指定DataFrame后追加

        Remark: 
            当前历史分位是对给定时间范围内的数据进行历史排位; history_time_ratio2采用当前时间的历史分位由此向前追溯到给定日期范围内进行历史排位,每一个bar单独计算,
        """        
        df_append= pd.DataFrame()
        if trace_back_months == 'all':
            df_selected_history = self.symbol_data
        else:
            years, months = divmod(trace_back_months, 12)
            cutoff_date = self.symbol_data['date'].max() - relativedelta(years=years, months=months)
            df_selected_history = self.symbol_data.loc[self.symbol_data['date'] >= cutoff_date]
        df_append['date'] = df_selected_history['date']
        if mode=='time':
            value_field = field + '历史时间百分位'
            rank_field = field + '历史时间分位'
            df_append[value_field] = df_selected_history[field].rank(method='min', ascending=True)
            rank_count = len(df_append[value_field].dropna())
            df_append[value_field] = df_append[value_field] / rank_count
            quantiles = np.percentile(df_append[value_field].dropna(), quantiles)
        elif mode=='value':
            value_field = field + '历史数值百分位'
            rank_field = field + '历史数值分位'
            max_value = df_selected_history[field].max()
            min_value = df_selected_history[field].min()
            scope = max_value - min_value
            df_append[value_field] = (df_selected_history[field] - min_value) / scope
            quantiles = list(map(lambda x: x/100, quantiles))
        else:
            None
        df_append[rank_field] = pd.cut(df_append[value_field].dropna(), bins=quantiles, labels=ranks, include_lowest=True, duplicates='drop', right=False)
        if df_rank.empty:
            df_rank = df_append
        else:
            df_rank = pd.merge(df_rank, df_append, on='date', how='outer')
        return df_rank
    
    def history_time_ratio2(self, field, df_rank=None, mode='time', trace_back_months='all', quantiles=[0, 20, 40, 60, 80, 100], ranks=[1, 2, 3, 4, 5]):
        '''history_time_ratio2采用当前时间的历史分位由此向前追溯到给定日期范围内进行历史排位,每一个bar单独计算,其他与history_time_ratio相同
        '''
        df_append= pd.DataFrame()
        df_append['date'] = self.symbol_data['date']
        if trace_back_months == 'all':
            window_size = len(self.symbol_data)
        else:
            window_size = trace_back_months * 20  # assuming 30 days per month
        if mode=='time':
            value_field = field + '历史时间百分位'
            rank_field = field + '历史时间分位'
            df_append[value_field] = self.symbol_data[field].rolling(window=window_size, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
            quantiles = np.percentile(df_append[value_field].dropna(), quantiles)
        elif mode=='value':
            value_field = field + '历史数值百分位'
            rank_field = field + '历史数值分位'
            df_append[value_field] = self.symbol_data[field].rolling(window=window_size, min_periods=1).apply(lambda x: (x[-1] - np.min(x)) / (np.max(x) - np.min(x)))
            quantiles = list(map(lambda x: x/100, quantiles))
        else:
            None
        df_append[rank_field] = pd.cut(df_append[value_field].dropna(), bins=quantiles, labels=ranks, include_lowest=True, duplicates='drop', right=False)
        # df_append.loc[:window_size-1, rank_field] = 0.5
        if df_rank.empty:
            df_rank = df_append
        else:
            df_rank = pd.merge(df_rank, df_append, on='date', how='outer')
        df_rank = pd.merge(df_rank, self.symbol_data[['date', field]], on='date', how='outer')
        return df_rank

    def calculate_data_rank(self, data_list=['库存', '仓单', '持仓量', '现货利润', '盘面利润'], trace_back_months='all'):
        """计算一组数据的历史分位数,

        Args:
            data_list (list): 字符串列表,代表 `symbol_data` 中的字段名称,函数将对这些字段进行历史分位数的计算,
            trace_back_months (str/int): 定义了计算历史百分位时使用的历史数据范围,默认为 'all',即使用全部历史数据；如果是整数,表示向前追溯使用的月份数量,
        Returns:
            DataFrame: 返回包含历史分位数的 DataFrame,
        """
        self.basis_color['基差率颜色'] = self.symbol_data['基差率'] > 0
        self.basis_color['基差率颜色'] = self.basis_color['基差率颜色'].replace({True:1, False:0})
        df_rank = pd.DataFrame()
        for field in data_list:
            df_rank = self.history_time_ratio2(field, df_rank=df_rank, trace_back_months=trace_back_months)
        self.data_rank = df_rank
        return self.data_rank

    def dominant_months(self, year, month, previous_monts=2):
        """计算主力合约月份的前几个月的日期范围,
        一般情况下,主力合约在进入交割月之前的2个月遵循产业逻辑进行修复基差,因此这段时间非常适合进行以基差分析为基础的交易,

        Args:
            year (int): 主力合约的年份,
            month (int): 主力合约的月份,
            previous_monts (int): 需要向前追溯的月份数量,默认为2,
        Returns:
            tuple: 返回开始日期和结束日期,
        """
        # 创建一个日期对象,代表主力合约月份的第一天
        contract_date = datetime(year, month, 1)
        # 使用dateutil的relativedelta函数,计算两个月前的日期
        start_date = contract_date - relativedelta(months=previous_monts)
        # 计算结束日期,即主力合约月份的前一天
        end_date = contract_date - relativedelta(days=1)
        return start_date, end_date
    
    def get_spot_months(self):
        '''根据主力合约的月份,生成起对应的现货月序列

        Returns:
            无返回值,结果保存在类成员变量spot_months中
        '''        
        dominant_months = self.symbol_setting['DominantMonths']
        years = self.symbol_data['date'].dt.year.unique()
        self.spot_months = pd.DataFrame(columns=['Year', 'Contract Month', 'Start Date', 'End Date'])
        for year in years:
            for month in dominant_months:
                start_date, end_date = self.dominant_months(year, month)
                new_row = pd.DataFrame({'Year': [year], 'Contract Month': [month], 'Start Date': [start_date], 'End Date': [end_date]})
                # if not new_row.isnull().all().all():
                self.spot_months = pd.concat([self.spot_months, new_row], ignore_index=True)
    
    def get_profits(self, symbol_chain):
        """
        此函数用于计算商品的现货利润和盘面利润。

        Args:
        symbol_chain:SymbolChain 对象,包含了产业链中该商品上游原材料的相关信息。

        Returns
        返回一个 DataFrame,包含以下列:
        'date':日期
        '现货利润':现货价格减去原材料现货成本和其他成本
        '盘面利润':主力合约结算价减去原材料盘面成本和其他成本

        此外,此函数还会更新 self.symbol_data,将计算得到的现货利润和盘面利润添加到其中。
        """        
        if 'ProfitFormula' not in self.symbol_setting:
            pass

        profit_formula = self.symbol_setting['ProfitFormula']
        cost_factors = profit_formula['Factor']

        #df_spot_price = symbol.symbol_data[['date', '现货价格']]
        df_price = self.symbol_data[['date', '现货价格', '主力合约结算价']]

        # df_raw_materials = pd.DataFrame()
        df_raw_materials = pd.DataFrame(columns=['date', '原材料现货成本总和', '原材料盘面成本总和'])
        first_combine = True
        
        for raw_material, multiplier in cost_factors.items():
            df_raw_material = symbol_chain.get_symbol(raw_material).symbol_data[['date', '现货价格', '主力合约结算价']].copy()
            # df_raw_material.dropna(axis=0, how='all', subset=['现货价格', '主力合约结算价'], inplace=True)
            df_raw_material['现货成本'] = df_raw_material['现货价格'] * multiplier
            df_raw_material['盘面成本'] = df_raw_material['主力合约结算价'] * multiplier
            df_raw_materials = pd.merge(df_raw_materials, df_raw_material, 
                                        on='date', how='outer')
            if first_combine:
                df_raw_materials['原材料现货成本总和'] = df_raw_materials['现货成本']
                df_raw_materials['原材料盘面成本总和'] = df_raw_materials['盘面成本']     
                first_combine = False   
            #     df_raw_materials['原材料现货成本总和'] = 0
            #     df_raw_materials['原材料盘面成本总和'] = 0
            else:
            #     df_raw_materials['原材料现货成本总和'].fillna(0, inplace=True)
            #     df_raw_materials['原材料盘面成本总和'].fillna(0, inplace=True)
                df_raw_materials['原材料现货成本总和'] = df_raw_materials['原材料现货成本总和'] + df_raw_materials['现货成本']
                df_raw_materials['原材料盘面成本总和'] = df_raw_materials['原材料盘面成本总和'] + df_raw_materials['盘面成本']
            df_raw_materials= df_raw_materials[['date', '原材料现货成本总和', '原材料盘面成本总和']]
            
        df_profit = pd.merge(df_raw_materials, df_price, on='date', how='outer')
        df_profit['现货利润'] = df_profit['现货价格'] - df_profit['原材料现货成本总和']- profit_formula['其他成本']
        df_profit['盘面利润'] = df_profit['主力合约结算价'] - df_profit['原材料盘面成本总和']- profit_formula['其他成本']
        df_profit = df_profit[['date', '现货利润', '盘面利润']].dropna(axis=0, how='all', subset=['现货利润', '盘面利润'])
        self.symbol_data = pd.merge(self.symbol_data, df_profit, on='date', how='outer')
        return df_profit

    def get_signals(self, selected_index=[]):
        """
        此函数用于计算指定指标的信号。

        Args:
        selected_index:一个字符串列表,代表 `symbol_data` 中的字段名称,函数将对这些字段进行信号的计算。

        Returns:
        返回一个 DataFrame,包含以下列:
        'date':日期
        '基差率':基差率的信号,规则化处理:大于0为1,小于0为-1,等于0为0
        '库存历史时间分位':库存历史时间分位的信号,规则化处理:等于5为-1,等于1为1,其他为0
        '仓单历史时间分位':仓单历史时间分位的信号,规则化处理同上
        '现货利润历史时间分位':现货利润历史时间分位的信号,规则化处理同上
        '盘面利润历史时间分位':盘面利润历史时间分位的信号,规则化处理同上
        '库存|仓单':库存历史时间分位和仓单历史时间分位的信号,两者中任一为1则为1,否则为0
        '现货利润|盘面利润':现货利润历史时间分位和盘面利润历史时间分位的信号,两者中任一为1则为1,否则为0
        '信号数量':所有选定指标的信号之和

        此外,此函数还会更新 self.signals,将计算得到的信号添加到其中。
        """        
        if self.signals.empty:
            self.signals = pd.merge(self.symbol_data[['date', '基差率']],
                                    self.data_rank[['date', '库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位']],
                                    on='date', how='outer')
            self.signals['基差率'] = self.signals['基差率'].map(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))            
            # For other columns
            for col in ['库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位']:
                self.signals[col] = self.signals[col].map(lambda x: -1 if x == 5 else (0 if x != 1 else 1)).fillna(0).astype(int)
            self.signals['库存|仓单'] = self.signals['库存历史时间分位'] | self.signals['仓单历史时间分位']
            self.signals['现货利润|盘面利润'] = self.signals['现货利润历史时间分位'] | self.signals['盘面利润历史时间分位']
        if len(selected_index)!=0:
            self.signals['信号数量'] = self.signals[selected_index].sum(axis=1)
        return self.signals
    
    def prepare_data(self, trace_back_months=60):
        self.merge_data()
        self.get_profits()
        self.calculate_data_rank(trace_back_months)

class SymbolFigure:
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.look_forward_months = 0
        self.main_figure = {}
        trade_date = ak.tool_trade_date_hist_sina()['trade_date']
        trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
        dt_all = pd.date_range(start=symbol.symbol_data['date'].iloc[0],end=symbol.symbol_data['date'].iloc[-1])
        dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
        self.trade_breaks = list(set(dt_all) - set(trade_date))
        
    def create_figure(self, show_index=[], mark_cycle=[], sync_index=[], look_forward_months='all'):
        symbol = self.symbol
        if look_forward_months != self.look_forward_months:
            # print('Redraw look-forward history data:', look_forward_months)
            symbol.calculate_data_rank(trace_back_months=look_forward_months)
            self.look_forward_months = look_forward_months
    
        fig_rows = len(show_index) + 1
        specs = [[{"secondary_y": True}] for _ in range(fig_rows)]
        row_widths = [0.1] * (fig_rows - 1) + [0.5]
        subtitles = ['现货/期货价格'] + show_index
        self.main_figure = make_subplots(rows=fig_rows, cols=1, specs=specs, row_width=row_widths, subplot_titles=subtitles, shared_xaxes=True, vertical_spacing=0.02)
        # 创建主图:期货价格、现货价格、基差
        main_figure = self.main_figure
        fig_future_price = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['主力合约收盘价'], name='期货价格', 
                                    marker_color='rgb(84,134,240)')
        fig_spot_price = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货价格'], name='现货价格', marker_color='rgba(105,206,159,0.4)')
        fig_basis = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['基差'], stackgroup='one', name='基差', 
                            marker=dict(color='rgb(239,181,59)', opacity=0.4), showlegend=False) 
        key_mark_sync_index = '指标共振周期'
        if key_mark_sync_index in mark_cycle:
            df_signals =symbol.get_signals(sync_index)
            signal_nums = len(sync_index)
            df_signals.loc[~((df_signals['信号数量'] == signal_nums) | (df_signals['信号数量'] == -signal_nums)), '信号数量'] = np.nan
            df_signals['位置偏移'] = df_signals['信号数量'].replace([signal_nums, -signal_nums], [0.99, 1.01])
            df_signals['绝对位置'] = df_signals['位置偏移'] * symbol.symbol_data['主力合约收盘价']
            signal_color_mapping ={1.01:'green', 0.99:'red'}
            df_signals['信号颜色'] = df_signals['位置偏移'].map(signal_color_mapping)
            fig_signal = go.Scatter(x=df_signals['date'], y=df_signals['绝对位置'], name='信号', mode='markers', showlegend=False,
                                    marker=dict(size=4, color=df_signals['信号颜色'], colorscale=list(signal_color_mapping.values())))
            main_figure.add_trace(fig_signal, row=1, col=1)        
        main_figure.add_trace(fig_basis, row = 1, col = 1, secondary_y=True) 
        main_figure.add_trace(fig_future_price, row = 1, col = 1)
        main_figure.add_trace(fig_spot_price, row = 1, col = 1)
        
        sub_index_rows = 2
        # 创建副图-基差率,并根据基差率正负配色
        key_basis_rate = '基差率'
        if key_basis_rate in show_index:
            sign_color_mapping = {0:'green', 1:'red'}
            fig_basis_rate = go.Bar(x=symbol.symbol_data['date'], y = symbol.symbol_data['基差率'], name=key_basis_rate,
                                    marker=dict(color=symbol.basis_color['基差率颜色'], colorscale=list(sign_color_mapping.values()),
                                                showscale=False),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_basis_rate, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        histroy_color_mapping ={1:'red', 2:'gray', 3:'gray', 4:'gray', 5:'green'}
        # 创建副图-库存
        key_storage = '库存'
        if key_storage in show_index:
            fig_storage = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['库存'], name=key_storage, marker_color='rgb(239,181,59)', showlegend=False,)
            # fig_storage = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['库存'], name='库存', mode='markers', marker=dict(size=2, color='rgb(239,181,59)'))
            symbol.data_rank['库存分位颜色'] = symbol.data_rank['库存历史时间分位'].map(histroy_color_mapping)
            # fig_storage_rank = go.Bar(x=df_rank['date'], y=df_rank['库存历史时间百分位'], name='库存分位', marker_color='rgb(234,69,70)')
            fig_storage_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['库存历史时间百分位'], name='库存分位', 
                                    marker=dict(color=symbol.data_rank['库存分位颜色'], opacity=0.6),
                                    showlegend=False,
                                    hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_storage_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_storage, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-仓单
        key_receipt = '仓单'
        if key_receipt in show_index:
            fig_receipt = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['仓单'], name=key_receipt, marker_color='rgb(239,181,59)', showlegend=False,)
            # symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
            # fig_receipt_rank = go.Scatter(x=symbol.data_rank['date'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位', marker_color='rgb(239,181,59)')
            symbol.data_rank['仓单分位颜色'] = symbol.data_rank['仓单历史时间分位'].map(histroy_color_mapping)
            fig_receipt_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['仓单历史时间百分位'], name='仓单分位',
                                        marker=dict(color=symbol.data_rank['仓单分位颜色'], opacity=0.6),
                                        showlegend=False,
                                        hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_receipt_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_receipt, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-持仓量
        key_open_interest = '持仓量'
        if key_open_interest in show_index:
            fig_open_interest = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['持仓量'], name=key_receipt, marker_color='rgb(239,181,59)', showlegend=False,)
            symbol.data_rank['持仓量分位颜色'] = symbol.data_rank['持仓量历史时间分位'].map(histroy_color_mapping)
            fig_open_interest_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['持仓量历史时间百分位'], name='持仓量分位',
                                            marker=dict(color=symbol.data_rank['持仓量分位颜色'], opacity=0.6),
                                            showlegend=False,
                                            hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_open_interest_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_open_interest, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1            

        # 创建副图-现货利润
        key_spot_profit = '现货利润'
        if key_spot_profit in show_index:
            # fig_spot_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货利润'], name='现货利润', mode='markers', marker=dict(size=2, color='rgb(234,69,70)'))
            fig_spot_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['现货利润'], name=key_spot_profit, marker_color='rgb(239,181,59)', showlegend=False,)
            symbol.data_rank['现货利润分位颜色'] = symbol.data_rank['现货利润历史时间分位'].map(histroy_color_mapping)
            fig_spot_profit_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['现货利润历史时间百分位'], name='现货利润', 
                                        marker=dict(color=symbol.data_rank['现货利润分位颜色'], opacity=0.6),
                                        showlegend=False,
                                        hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_spot_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_spot_profit, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 创建副图-盘面利润
        key_future_profit = '盘面利润'
        if key_future_profit in show_index:
            fig_future_profit = go.Scatter(x=symbol.symbol_data['date'], y=symbol.symbol_data['盘面利润'], name=key_future_profit, marker_color='rgb(239,181,59)', showlegend=False,)
            symbol.data_rank['盘面利润分位颜色'] = symbol.data_rank['盘面利润历史时间分位'].map(histroy_color_mapping)
            fig_future_profit_rank = go.Bar(x=symbol.data_rank['date'], y=symbol.data_rank['盘面利润历史时间百分位'], name='盘面利润 ', 
                                            marker=dict(color=symbol.data_rank['盘面利润分位颜色'], opacity=0.6),
                                            showlegend=False,
                                            hovertemplate='%{y:.2%}')
            main_figure.add_trace(fig_future_profit_rank, row = sub_index_rows, col = 1, secondary_y=True)
            main_figure.add_trace(fig_future_profit, row = sub_index_rows, col = 1)
            sub_index_rows = sub_index_rows + 1

        # 用浅蓝色背景标记现货月时间范围
        key_mark_spot_months = '现货交易月'
        if key_mark_spot_months in mark_cycle:
            main_figure.update_layout(shapes=[])   
            for _, row in symbol.spot_months.iterrows():
                main_figure.add_shape(
                    # 矩形
                    type="rect",
                    x0=row['Start Date'], x1=row['End Date'],
                    y0=0, y1=1,
                    xref='x', yref='paper',
                    fillcolor="LightBlue", opacity=0.1,
                    line_width=0,
                    layer="below"
                )
        else:
            # shapes = main_figure.layout.shapes
            # shapes[0]['line']['width'] = 0
            main_figure.update_layout(shapes=[])
        # 图表初始加载时,显示最近一年的数据
        one_year_ago = datetime.now() - timedelta(days=365)
        date_now = datetime.now().strftime('%Y-%m-%d')
        date_one_year_ago = one_year_ago.strftime('%Y-%m-%d')
        # X轴坐标按照年-月显示
        main_figure.update_xaxes(
            showgrid=False,
            zeroline=True,
            dtick="M1",  # 按月显示
            ticklabelmode="instant",   # instant  period
            tickformat="%m\n%Y",
            rangebreaks=[dict(values=self.trade_breaks)],
            rangeslider_visible = False, # 下方滑动条缩放
            range=[date_one_year_ago, date_now],
            # 增加固定范围选择
            rangeselector = dict(
                buttons = list([
                    dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
                    dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
                    # dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),                
                    dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
                    dict(step = 'all')
                    ]))
        )
        main_figure.update_yaxes(
            showgrid=False,
        )
        #main_figure.update_traces(xbins_size="M1")
        max_y = symbol.symbol_data['主力合约收盘价'] .max() * 1.05
        min_y = symbol.symbol_data['主力合约收盘价'] .min() * 0.95
        main_figure.update_layout(
            yaxis_range=[min_y,max_y],
            #autosize=False,
            #width=800,
            height=1200,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='WhiteSmoke',  
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=1,
                xanchor='left',
                x=0,
                bgcolor='WhiteSmoke',
                bordercolor='LightSteelBlue',
                borderwidth=1
            )
        )
        return main_figure
