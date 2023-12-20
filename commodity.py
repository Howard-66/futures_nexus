import json
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
from dateutil.relativedelta import relativedelta,MO
import akshare as ak
from functools import reduce

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
        
    def initialize_data(self):
        for _, symbol in self.symbol_dict.items():
            df = symbol.merge_data()
        
class SymbolData:
    """品种数据类:
        用于品种对应的数据更新、加载、预处理和访问
    """
    
    def __init__(self, id, name, json_file, symbol_setting=''):
        """
        SymbolData类的构造函数。
    
        Args:
            id (str): 品种ID，商品期货为英文简写，例如：螺纹钢为'RB'。
            name (str): 品种中文名称，例如：螺纹钢。
            json_file (str): 品种对应的json文件，主要存储品种的数据索引内容，使用工作目录的相对路径，同一个产业链使用统一的配置文件。
            symbol_setting (str, optional): 符号设置的字典。默认为空。
    
        Returns:
            SymbolData: 返回SymbolData对象，如果未提供id、name和配置文件，则返回空
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
        更新配置文件的内容。    
        Args:
            symbol_setting (dict): 符号设置的字典。
    
        Raises:
            IOError: 如果读取或写入配置文件时发生错误，则抛出IOError异常。
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
            - 原文件第一行为“宏观数据“或类似内容，但read_excel方法未加载该行内容
            - 数据的第一行作为指标标题
            - 第一列作为日期
            - 前四行和最后一行都不是数据内容
            - 剔除“日期”字段为空的行和其他非数据内容（标识数据来源的文字内容）
            
            Choice文件导出注意事项：
            - 导出字段选择：指标名称、频率、单位、来源
            - 日期排序：降序
            - 图形设置：不导出图形
            - 勾选“使用函数方式导出”
        Args:
            file_path (str): Choice导出文件(.xlsx)的绝对路径

        Returns:
            dataframe: 将Choice导出文件内容加载到dataframe，并返回
        """
        if file_path=='':
            return None
        df = pd.read_excel(file_path)
        df.columns = df.iloc[0]
        df.rename(columns={df.columns[0]: '日期'}, inplace=True)
        df = df[4:]
        df.reset_index(drop=True, inplace=True)
        df.dropna(axis=0, subset=['日期'], inplace=True)
        df = df[df['日期'] != '数据来源：东方财富Choice数据']
        df['日期'] = pd.to_datetime(df['日期'])
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
        df.rename(columns={'date': '日期'}, inplace=True)
        # TODO：其他数据格式化
        return df

    def update_akshare_file(self, mode='append', start_date='', end_date=''):
        """通过AKShare接口更新历史数据

        Args:
            mode (str, optional): 更新模式. 默认值为 'append'.
            - initial: 根据指定的时间段初始创建数据文件，后续使用period模式向前补充、append模式向后补充
            - append: 根据文件最后记录，更新到当前日期，会覆盖更新历史数据中的最后一条记录
            - period: 仅更新指定时间段的数据（目前仅支持向前追加，不做去重）
            - all: 全部更新，并覆盖原数据\n
            start_date (str, optional): 数据更新的起始日期\n
            end_date (str, optional): 数据更新的默认日期.

        Returns:
            dataframe: 将新增数据与原数据合并并返回，同时保存至文件
        """
        basis_file = self.symbol_setting['DataIndex']['现货价格']['Path']
        if mode == 'append':
            df_basis = pd.read_excel(basis_file)
            df_basis.reset_index(drop=True, inplace=True)
            today = datetime.now().strftime("%Y%m%d")
            last_date = str(df_basis.iloc[-1]['date'])
            df_append = ak.futures_spot_price_daily(start_day=last_date, end_day=today, vars_list=[self.id])
            # 移除最后一条重复数据，用最新数据替代
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
                # TODO: #目前仅支持向前补充数据，待增加与已有数据重叠更新（数据去重）
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

    def merge_data(self):
        """对数据索引中引用到的数据进行合并
            根据数据源（Choice/AKShare）调用对应的文件加载方法，并按照约定格式化数据，日期数据格式化为datatime，并按照升序排列，对应日期确实数据的置位NaN。
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
                elif data_source=='AKShare':
                    locals()[df_name] = self.load_akshare_file(value_items['Path'])
                else:
                    pass
                column_dict[df_name] = ['日期']
            column_dict[df_name].append(value_items['Field'])
        for df_key in column_dict:
            locals()[df_key] = locals()[df_key][column_dict[df_key]]
            data_frames.append(locals()[df_key])
        self.symbol_data = reduce(lambda left,right: pd.merge(left,right,on='日期', how='outer'), data_frames)
        for key in data_index:
            self.symbol_data.rename(columns={data_index[key]['Field']:key}, inplace=True)
        self.symbol_data.sort_values(by='日期', ascending=True, inplace=True)
        # self.symbol_data['库存'] = self.symbol_data['库存'].fillna(method='ffill', limit=None)
        self.symbol_data['库存'] = self.symbol_data['库存'].ffill()
        if '基差' not in data_index:
            self.symbol_data['基差'] = self.symbol_data['现货价格'] - self.symbol_data['主力合约结算价']
            self.symbol_data['基差率'] = self.symbol_data['基差'] / self.symbol_data['现货价格']
        return self.symbol_data
    
    def history_time_ratio(self, field, df_rank = None, mode='time', trace_back_months='all', quantiles=[0, 20, 40, 60, 80, 100], ranks=[1, 2, 3, 4, 5]):
        """返回指定数据序列的历史分位
            计算数据在序列中的历史数值百分位或时间百分位，并根据区间划定分位.
        Args:
            - field (str): symbol_data中的字段名称
            - df_rank (DataFrame, optional): 指定用于存储返回结果的DataFrame. 默认为空：创建DataFrame并返回；不为空时直接追加“历史百分位”、“历史分位”两列结果.
            - mode (str, optional): 计算模式. 'time'：默认值，计算数据在序列中的时间百分位；'value'：根据数据在序列中的最大值最小值范围，确定百分位.
            - trace_back_months (str/int, optional): 计算历史百分位时使用的历史数据范围。默认为all，即使用全部历史数据；为整数时，指定向前追溯使用的月份数量. 
            - quantiles (list, optional): 分位分区. 默认分区为 [0, 20, 40, 60, 80, 100].
            - ranks (list, optional): 分区标签. 默认为 [1, 2, 3, 4, 5].

        Returns:
            DataFrame: df_rank为空时，创建并返回一个新的DataFrame，包含“历史百分位”、“历史分位”两列结果；不为空时在指定DataFrame后追加
        """        
        df_append= pd.DataFrame()
        if trace_back_months == 'all':
            df_selected_history = self.symbol_data
        else:
            years, months = divmod(trace_back_months, 12)
            cutoff_date = self.symbol_data['日期'].max() - relativedelta(years=years, months=months)
            df_selected_history = self.symbol_data.loc[self.symbol_data['日期'] >= cutoff_date]
        df_append['日期'] = df_selected_history['日期']
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
            df_rank = pd.merge(df_rank, df_append, on='日期', how='outer')
        return df_rank

    def calculate_data_rank(self, data_list=['库存', '仓单', '现货利润', '盘面利润'], trace_back_months='all'):
        """计算一组数据的历史分位数。

        Args:
            data_list (list): 字符串列表，代表 `symbol_data` 中的字段名称，函数将对这些字段进行历史分位数的计算。
            trace_back_months (str/int): 定义了计算历史百分位时使用的历史数据范围。默认为 'all'，即使用全部历史数据；如果是整数，表示向前追溯使用的月份数量。
        Returns:
            DataFrame: 返回包含历史分位数的 DataFrame。
        """
        self.basis_color['基差率颜色'] = self.symbol_data['基差率'] > 0
        self.basis_color['基差率颜色'] = self.basis_color['基差率颜色'].replace({True:1, False:0})
        for field in data_list:
            self.data_rank  = self.history_time_ratio(field, df_rank=self.data_rank, trace_back_months=trace_back_months)
        return self.data_rank

    def dominant_months(self, year, month, previous_monts=2):
        """计算主力合约月份的前几个月的日期范围。
        一般情况下,主力合约在进入交割月之前的2个月遵循产业逻辑进行修复基差,因此这段时间非常适合进行以基差分析为基础的交易。

        Args:
            year (int): 主力合约的年份。
            month (int): 主力合约的月份。
            previous_monts (int): 需要向前追溯的月份数量,默认为2。
        Returns:
            tuple: 返回开始日期和结束日期。
        """
        # 创建一个日期对象，代表主力合约月份的第一天
        contract_date = datetime(year, month, 1)
        # 使用dateutil的relativedelta函数，计算两个月前的日期
        start_date = contract_date - relativedelta(months=previous_monts)
        # 计算结束日期，即主力合约月份的前一天
        end_date = contract_date - relativedelta(days=1)
        return start_date, end_date
    
    def get_spot_months(self):
        dominant_months = self.symbol_setting['DominantMonths']
        years = self.symbol_data['日期'].dt.year.unique()
        self.spot_months = pd.DataFrame(columns=['Year', 'Contract Month', 'Start Date', 'End Date'])
        for year in years:
            for month in dominant_months:
                start_date, end_date = self.dominant_months(year, month)
                new_row = pd.DataFrame({'Year': [year], 'Contract Month': [month], 'Start Date': [start_date], 'End Date': [end_date]})
                self.spot_months = pd.concat([self.spot_months, new_row], ignore_index=True)
    
    def get_profits(self, symbol_chain):
        if 'ProfitFormula' not in self.symbol_setting:
            pass

        profit_formula = self.symbol_setting['ProfitFormula']
        cost_factors = profit_formula['Factor']

        #df_spot_price = symbol.symbol_data[['日期', '现货价格']]
        df_price = self.symbol_data[['日期', '现货价格', '主力合约结算价']]

        # df_raw_materials = pd.DataFrame()
        df_raw_materials = pd.DataFrame(columns=['日期', '原材料现货成本总和', '原材料盘面成本总和'])
        first_combine = True
        for raw_material, multiplier in cost_factors.items():
            df_raw_material = symbol_chain.get_symbol(raw_material).symbol_data[['日期', '现货价格', '主力合约结算价']].copy()
            df_raw_material.dropna(axis=0, how='all', subset=['现货价格', '主力合约结算价'], inplace=True)
            df_raw_material['现货成本'] = df_raw_material['现货价格'] * multiplier
            df_raw_material['盘面成本'] = df_raw_material['主力合约结算价'] * multiplier
            df_raw_materials = pd.merge(df_raw_materials, df_raw_material, 
                                        on='日期', how='outer')
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
            df_raw_materials= df_raw_materials[['日期', '原材料现货成本总和', '原材料盘面成本总和']]

        df_profit = pd.merge(df_raw_materials, df_price, on='日期', how='outer')
        df_profit['现货利润'] = df_profit['现货价格'] - df_profit['原材料现货成本总和']- profit_formula['其他成本']
        df_profit['盘面利润'] = df_profit['主力合约结算价'] - df_profit['原材料盘面成本总和']- profit_formula['其他成本']
        df_profit = df_profit[['日期', '现货利润', '盘面利润']].dropna(axis=0, how='all', subset=['现货利润', '盘面利润'])
        self.symbol_data = pd.merge(self.symbol_data, df_profit, on='日期', how='outer')
        return df_profit

    def get_signals(self, selected_index=[]):
        if self.signals.empty:
            self.signals = pd.merge(self.symbol_data[['日期', '基差率']],
                                    self.data_rank[['日期', '库存历史时间分位', '仓单历史时间分位', '现货利润历史时间分位', '盘面利润历史时间分位']],
                                    on='日期', how='outer')
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
    
# 定义一个子类，继承商品类
class MetalSymbolData(SymbolData):
    # 定义构造方法，初始化子类的属性
    def __init__(self, id, name, config_file, discount):
        # 调用父类的构造方法，初始化父类的属性
        super().__init__(id, name, config_file)
        # 添加子类特有的属性，折扣率
        self.discount = discount

    # 重写父类的merge_data方法
    def merge_data(self):
        return None

