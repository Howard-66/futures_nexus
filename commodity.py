import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta,MO
import akshare as ak

# 定义一个商品类
class SymbolData:
    # 定义构造方法，初始化商品的基本属性
    def __init__(self, id, name, json_file):
        if json_file == '':
            return None
        self.id = id # 商品号
        self.name = name # 商品名
        with open(json_file, encoding='utf-8') as config_file:
            self.data_index = json.load(config_file)[self.name]
        self.history = [] # 商品历史价格数据，用列表存储

    # 读取choice数据终端导出的数据文件
    """
        读取Choice导出的数据文件并按照约定规则格式化
        处理规则：
        1、数据的第一行作为指标标题
        2、第一列作为日期
        3、前四行和最后一行都不是数据内容
        4、中间可能存在空行 
    """
    # TODO: 注意数据文件多次更新后，文件尾部的内容变化
    def load_choice_file(self, file_path):
        if file_path=='':
            return None
        df = pd.read_excel(file_path)
        df.columns = df.iloc[0]
        df.rename(columns={df.columns[0]: '日期'}, inplace=True)
        df = df[4:-1]
        df.reset_index(drop=True, inplace=True)
        df.dropna(axis=0, subset=['日期'], inplace=True)
        return df
    
    # 读取通过AK Share接口下载保存的数据文件
    def load_akshare_file(self, type):
        if type == '':
            return None
        file_path = self.data_index[type]['Path']
        df = pd.read_excel(file_path)
        # 格式化日期
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        # TODO：其他数据格式化
        return df

    def update_akshare_file(self, mode='append', start_date='', end_date=''):
        basis_file = self.data_index['现货价格']['Path']
        df_basis = pd.read_excel(basis_file)
        # 删除多余的列
        # df_basis.drop(['Unnamed: 0.2', 'Unnamed: 0.1', 'Unnamed: 0'], axis=1, inplace=True)
        if mode == 'append':
            today = datetime.now().strftime("%Y%m%d")
            last_date = str(df_basis.iloc[-1]['date'])
            df_append = ak.futures_spot_price_daily(start_day=last_date, end_day=today, vars_list=[self.id])
            df_basis.iloc[-1] = df_append.iloc[0]
            df_basis =pd.concat([df_basis, df_append[1:]])
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
