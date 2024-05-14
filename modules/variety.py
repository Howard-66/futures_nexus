# import numpy as np
import pandas as pd
import json
import re
from asteval import Interpreter
import dataworks as dw
import os
import time

class Variety:
    def __init__(self, id, name=''):
        if id =='':
            return None
        self.id = id # 商品ID（英文缩写）
        self.common_json = 'setting/common.json'
        self.variety_json = 'setting/variety.json'        
        # 从配置文件中获取data_index
        with open(self.common_json, encoding='utf-8') as common_file: 
            symbol_dataindex_setting = json.load(common_file)['DataIndex']
        with open(self.variety_json, encoding='utf-8') as variety_file:
            variety_setting = json.load(variety_file)[self.id]      
        variety_setting['DataIndex'] = {**symbol_dataindex_setting, **variety_setting['DataIndex']} if 'DataIndex' in variety_setting else symbol_dataindex_setting
        self.symbol_setting = variety_setting   
        self.trade_breaks = None
        self.data_source = None

    def _load_data_from_choice(self, path):
        """
        从ChoiceExcel文件中加载数据。
        """
        def __convert_excel_to_csv(file_path, header=1):
            """
            处理指定文件：如果是 .xlsx 文件且不存在同名的 .csv 文件，则进行转换并返回内容；
            如果是 .csv 文件，直接读取并返回内容。
            """
            file_dir, file_name = os.path.split(file_path)
            file_base, file_ext = os.path.splitext(file_name)
            
            if file_ext == '.csv':
                # 读取 csv 文件
                df = pd.read_csv(file_path, header=header)
            elif file_ext == '.xlsx':
                # 构建对应的 csv 文件路径
                csv_path = os.path.join(file_dir, file_base + '.csv')
                
                # 检查同名的 csv 文件是否存在
                if not os.path.exists(csv_path):
                    # 读取 xlsx 文件
                    df = pd.read_excel(file_path, engine='openpyxl')
                    # 保存为 csv 文件
                    df.to_csv(csv_path, index=False, header=header)
                else:
                    # 读取已存在的 csv 文件
                    df = pd.read_csv(csv_path, header=header)        
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return df        
        
        if not path:
            return None
        df = __convert_excel_to_csv(path, header=1)  # 利用header=1使得第2行（即索引1）作为列标题
        df = df[5:]  # 从第6行开始保留数据（因为header=1后，第二行已经变成了索引0）
        df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        df = df[df['date'].notna() & (df['date'] != '数据来源：东方财富Choice数据')]
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].notna()]
        df[df.select_dtypes(exclude=['datetime']).columns] = df.select_dtypes(exclude=['datetime']).apply(pd.to_numeric)        
        return df

    def load_data(self):
        def extract_variables(format_str):
            """从格式字符串中提取变量名"""
            # 正则表达式模式，匹配非空字符（即变量）
            variable_pattern = r'\w[\w:()%]*'
            # 使用正则表达式查找所有匹配的变量名
            variables = re.findall(variable_pattern, format_str)
            return variables  # 直接返回找到的变量名列表，无需额外处理
        
        column_dict= {}
        data_cache = {}
        data_index = self.symbol_setting['DataIndex']

        # def numpy_ffill(arr):
        #     """使用numpy实现向前填充（ffill）"""
        #     mask = np.isnan(arr)
        #     idx = np.where(~mask, np.arange(mask.size), 0)
        #     np.maximum.accumulate(idx, out=idx)
        #     return arr[idx]

        # def numpy_bfill(arr):
        #     """使用numpy实现向后填充（bfill）"""
        #     mask = np.isnan(arr)
        #     idx = np.where(~mask, np.arange(mask.size), mask.size - 1)
        #     idx = np.minimum.accumulate(idx[::-1])[::-1]
        #     return arr[idx]        

        # dws = gs.dataworks
        with dw.DataWorks() as dws:
            for key, value_items in data_index.items():
                # 按照配置文件中的DataFrame键值，将同类内容合并到同一张表中
                df_name = value_items['DataFrame']            
                fields = value_items['Field']
                variables_list = extract_variables(fields)
                if df_name in locals():        
                    # 键值是独立字段的，列名修改为key
                    if len(variables_list)==1:
                        locals()[df_name].rename(columns={variables_list[0]:key}, inplace=True)
                else:
                    # 未加载的数据，整表读取到df_name中
                    data_source = value_items['Source']
                    if data_source=='Choice':
                        locals()[df_name] = self._load_data_from_choice(value_items['Path'])
                    elif data_source=='SQLite':
                        locals()[df_name] = dws.get_data_by_symbol(value_items['Path'], self.id, '*')
                        locals()[df_name]['date'] = pd.to_datetime(locals()[df_name]['date'])
                    else:
                        continue
                    column_dict[df_name] = ['date']
                df = locals()[df_name]            
                if len(variables_list)==1:
                    # Field是独立字段的，列名修改为key
                    df.rename(columns={variables_list[0]:key}, inplace=True)
                    column_dict[df_name].append(key)
                else:                
                    # Field是公式表达的，进行解析计算
                    aeval = Interpreter()       
                    for var in variables_list:                    
                        safe_var = re.sub(r'[0-9:]', '', var)
                        df.rename(columns={var:safe_var}, inplace=True)                                     
                        aeval.symtable[safe_var] = df[safe_var]
                    safe_fields = re.sub(r'[0-9:]', '', fields)
                    df[key] = aeval.eval(safe_fields)
                    column_dict[df_name].append(key)
                # 根据配置中指定的填充方式填充缺失值
                if 'Transform' in value_items:
                    fill_na = value_items['Transform']
                    if fill_na=='Fill_Forward':
                        df[key] = df[key].ffill()
                        # df[key] = pd.Series(numpy_ffill(df[key].values))
                    elif fill_na=='Fill_Backward':
                        df[key] = df[key].bfill()
                        # df[key] = pd.Series(numpy_bfill(df[key].values))
                        # df[key] = df[key].infer_objects(copy=False)

            for df_key in column_dict:
                df = locals()[df_key]
                df = df[column_dict[df_key]]
                # 将column_dict中的各个key（除date外）作为date_cache的key,df作为value
                data_map = {key:df for key in column_dict[df_key][1:]}
                data_cache = {**data_cache, **data_map}
            # self.symbol_data = reduce(lambda left,right: pd.merge(left,right,on='date', how='outer'), data_frames)
            # self.symbol_data.sort_values(by='date', ascending=True, inplace=True)
            # 剔除非交易日数据
            # trade_date = dws.get_trade_date()
        dws.close()
        # valid_dates_mask = self.symbol_data['date'].isin(trade_date)
        # self.symbol_data.drop(self.symbol_data.index[~valid_dates_mask], inplace=True)                   
        self.data_source = data_cache
    
    def get_data(self, name):
        if name in self.data_source:
            return self.data_source[name][['date', name]].copy()
        else:
            return None
        
    def get_trade_breaks(self):
        if self.trade_breaks is None:
            dws = dw.DataWorks()
            trade_date = dws.get_trade_date()
            trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
            data = self.get_data('收盘价')
            dt_all = pd.date_range(start=data['date'].iloc[0],end=data['date'].iloc[-1])
            dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
            self.trade_breaks = list(set(dt_all) - set(trade_date))    
            dws.close()     
        return self.trade_breaks