import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta,MO
import akshare as ak

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
            self.data_index = json.load(config_file)[self.name]
        self.history = [] # 商品历史价格数据，用列表存储

    def load_choice_file(self, file_path):
        """读取choice数据终端导出的数据文件.
            Choiced导出文件格式对应的处理规则. 
            - 数据的第一行作为指标标题
            - 第一列作为日期
            - 前四行和最后一行都不是数据内容
            - 中间可能存在空行
            - TODO: 注意数据文件多次更新后，文件尾部的内容变化
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
        df = df[4:-1]
        df.reset_index(drop=True, inplace=True)
        df.dropna(axis=0, subset=['日期'], inplace=True)
        return df
    
    def load_akshare_file(self, file_path):
        """读取通过AK Share接口下载保存的数据文件

        Args:
            file_path (str): _description_

        Returns:
            _type_: _description_
        """
        if file_path == '':
            return None
        df = pd.read_excel(file_path)
        # 格式化日期
        # df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
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
        basis_file = self.data_index['现货价格']['Path']
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

    def merge_data(self, dfs):
        self.symbol_data = pd.merge(dfs[0], dfs[1], on='日期', how='outer')
        # TODO:
        return self.symbol_data

    # 定义一个方法，用于评估商品的价值，根据商品历史价格数据的平均值和标准差进行评估
    def evaluate_value(self):
        # 如果商品历史价格数据为空，返回None
        if len(self.history) == 0:
            return None
        # 否则，计算商品历史价格数据的平均值和标准差
        else:
            # 导入math模块，用于计算平方根
            import math
            # 计算平均值
            mean = sum(self.history) / len(self.history)
            # 计算标准差
            variance = sum([(x - mean) ** 2 for x in self.history]) / len(self.history)
            std = math.sqrt(variance)
            # 返回平均值和标准差的元组
            return (mean, std)

# 定义一个子类，继承商品类
class MetalSymbolData(SymbolData):
    # 定义构造方法，初始化子类的属性
    def __init__(self, id, name, config_file, discount):
        # 调用父类的构造方法，初始化父类的属性
        super().__init__(id, name, config_file)
        # 添加子类特有的属性，折扣率
        self.discount = discount

    # 重写父类的evaluate_value方法，根据折扣率计算商品的价值
    def evaluate_value(self):
        # 如果商品历史价格数据为空，返回None
        if len(self.history) == 0:
            return None
        # 否则，计算商品历史价格数据的平均值
        else:
            mean = sum(self.history) / len(self.history)
            # 根据折扣率计算商品的价值
            value = mean * (1 - self.discount)
            # 返回商品的价值
            return value
