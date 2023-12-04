import json
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta,MO
import akshare as ak
from functools import reduce

class SymbolData:
    """品种数据类:
        用于品种对应的数据更新、加载、预处理和访问
    """
    def __init__(self, id, name, json_file):
        """SymbolData构造函数\n
        根据品种配置信息构造SymbolData对象
        
        Args:
            id (str): 品种ID，商品期货为英文简写，例如：螺纹钢为'RB'\n
            name (str): 品种中文名称，例如：螺纹钢\n
            json_file (str): 品种对应的json文件，主要存储品种的数据索引内容，使用工作目录的相对路径，同一个产业链使用统一的配置文件
        
        Returns:
            SymbolData: 返回SymbolData对象，如果未提供id、name和配置文件，则返回空
        """
        if id =='' or name=='' or json_file == '':
            return None
        self.id = id # 商品号
        self.name = name # 商品名
        with open(json_file, encoding='utf-8') as config_file:
            self.symbol_setting = json.load(config_file)[self.name]

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
        df.rename(columns={'date': '日期'}, inplace=True)
        # TODO：其他数据格式化
        return df

    def update_akshare_file(self, mode='append', start_date='', end_date=''):
        """通过AKShare接口更新历史数据

        Args:
            mode (str, optional): 更新模式. 默认值为 'append'.
            - append: 根据文件最后记录，更新到当前日期，会覆盖更新历史数据中的最后一条记录
            - period: 仅更新制定时间段的数据（目前仅支持向前追加，不做去重）
            - all: 全部更新，并覆盖原数据\n
            start_date (str, optional): 数据更新的起始日期\n
            end_date (str, optional): 数据更新的默认日期.

        Returns:
            dataframe: 将新增数据与原数据合并并返回，同时保存至文件
        """
        basis_file = self.symbol_setting['DataIndex']['现货价格']['Path']
        df_basis = pd.read_excel(basis_file)
        df_basis.reset_index(drop=True, inplace=True)
        if mode == 'append':
            today = datetime.now().strftime("%Y%m%d")
            last_date = str(df_basis.iloc[-1]['date'])
            df_append = ak.futures_spot_price_daily(start_day=last_date, end_day=today, vars_list=[self.id])
            # 移除最后一条重复数据，用最新数据替代
            df_basis.drop(df_basis.shape[0]-1, inplace=True)
            df_basis =pd.concat([df_basis, df_append])
            df_basis.to_excel(basis_file)
            return df_basis
        elif mode=='period':
            if start_date=='' or end_date=='':
                return None
            df_period = ak.futures_spot_price_daily(start_day=start_date, end_day=end_date, vars_list=[self.id])
            df_basis =pd.concat([df_period, df_basis])
            # TODO: #目前仅支持向前补充数据，待增加与已有数据重叠更新（数据去重）
            df_basis.to_excel(basis_file)
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
                None
            else:
                data_source = value_items['Source']
                if data_source=='Choice':
                    locals()[df_name] = self.load_choice_file(value_items['Path'])
                elif data_source=='AKShare':
                    locals()[df_name] = self.load_akshare_file(value_items['Path'])
                else:
                    None
                column_dict[df_name] = ['日期']
            column_dict[df_name].append(value_items['Field'])
        for df_key in column_dict:
            locals()[df_key] = locals()[df_key][column_dict[df_key]]
            data_frames.append(locals()[df_key])
        self.symbol_data = reduce(lambda left,right: pd.merge(left,right,on='日期', how='outer'), data_frames)
        for key in data_index:
            self.symbol_data.rename(columns={data_index[key]['Field']:key}, inplace=True)
        self.symbol_data.sort_values(by='日期', ascending=True, inplace=True)
        # TODO: 通过AKShare获取的基差/基差率数据（螺纹钢）出现正负符号错误，其他品种待验证（如存在普遍现象，需要统一纠正）
        if '基差' not in data_index:
            self.symbol_data['基差'] = self.symbol_data['现货价格'] - self.symbol_data['主力合约结算价']
            self.symbol_data['基差率'] = self.symbol_data['基差'] / self.symbol_data['现货价格']
        return self.symbol_data
    
    def history_time_ratio(self, field, df_rank = None, mode='time', quantiles=[0, 20, 40, 60, 80, 100], ranks=[1, 2, 3, 4, 5]):
        """返回指定数据序列的历史分位
            计算数据在序列中的历史数值百分位或时间百分位，并根据区间划定分位.
        Args:
            - field (str): symbol_data中的字段名称
            - df_rank (DataFrame, optional): 指定用于存储返回结果的DataFrame. 默认为空：创建DataFrame并返回；不为空时直接追加“历史百分位”、“历史分位”两列结果.
            - mode (str, optional): 计算模式. 'time'：默认值，计算数据在序列中的时间百分位；'value'：根据数据在序列中的最大值最小值范围，确定百分位.
            - quantiles (list, optional): 分位分区. 默认分区为 [0, 20, 40, 60, 80, 100].
            - ranks (list, optional): 分区标签. 默认为 [1, 2, 3, 4, 5].

        Returns:
            DataFrame: df_rank为空时，创建并返回一个新的DataFrame，包含“历史百分位”、“历史分位”两列结果；不为空时在指定DataFrame后追加
        """
        if df_rank.empty:
            df_rank= pd.DataFrame()
        # df_rank['日期'] = self.symbol_data['日期']
        if mode=='time':
            value_field = field + '历史时间百分位'
            rank_field = field + '历史时间分位'
            df_rank[value_field] = self.symbol_data[field].rank(method='min', ascending=True)
            rank_count = len(df_rank[value_field].dropna())
            df_rank[value_field] = df_rank[value_field] / rank_count
            quantiles = np.percentile(df_rank[value_field].dropna(), quantiles)
        elif mode=='value':
            value_field = field + '历史数值百分位'
            rank_field = field + '历史数值分位'
            max_value = self.symbol_data[field].max()
            min_value=self.symbol_data[field].min()
            scope = max_value - min_value
            df_rank[value_field] = (self.symbol_data[field] - min_value) / scope
            quantiles = list(map(lambda x: x/100, quantiles))
        else:
            None
        df_rank[rank_field] = pd.cut(df_rank[value_field].dropna(), bins=quantiles, labels=ranks, include_lowest=True, duplicates='drop', right=False)
        return df_rank

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
