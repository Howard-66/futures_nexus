import pandas as pd
import sqlite3
import json
import akshare as ak
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
import threading


class DataWorks:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(DataWorks, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, db_uri='sqlite:///data/futures.db') -> None:
        # self.engine = create_engine(db_uri)
        # self.conn = self.engine.connect()
        self.engine = create_engine(
            db_uri,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.conn = self.engine.connect()
        # self.conn = sqlite3.connect('data/futures.db')
        self.variety_setting = None
        self.variety_json = 'setting/variety.json'
        self.variety_id_name_map = None
        self.variety_name_id_map = None
        self.trade_date = None
        
    def __enter__(self):
        self.conn = self.engine.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        # self.engine.dispose()
    
    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_data(self, table, condition='', fields='*'):
        fields_str = fields if fields == '*' or isinstance(fields, str) else ', '.join(fields)
        where_sql = f" WHERE {condition}" if condition else ""
        sql = f"SELECT {fields_str} FROM {table}{where_sql}"
        df = pd.read_sql_query(sql, self.conn)
        return df
        
    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_data_by_sql(self, sql):
        return pd.read_sql_query(sql, self.conn)

    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_data_by_symbol(self, table, symbol_id, fields='*'):
        condition = f"variety='{symbol_id}'"
        fields_str = fields if fields == '*' or isinstance(fields, str) else ', '.join(fields)
        sql = f"SELECT {fields_str} FROM {table} WHERE {condition}"
        df = pd.read_sql_query(sql, self.conn)
        return df

    def save_data(self, df, to_table, mode='replace'):
        df.to_sql(to_table, self.engine, if_exists=mode, index=False)

    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_last_date(self, table, symbol_id=None, date_field='date'):
        condition = f"WHERE variety='{symbol_id}'" if symbol_id else ""
        sql = f"SELECT MAX({date_field}) AS last_date FROM {table} {condition}"
        last_date = pd.read_sql_query(sql, self.conn).iloc[0, 0]
        return last_date

    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_trade_date(self):
        if self.trade_date is None:
            # 假设 ak.tool_trade_date_hist_sina() 提供了所需的交易日期数据
            trade_date = ak.tool_trade_date_hist_sina()['trade_date']
            self.trade_date = pd.to_datetime(trade_date)
        return self.trade_date

    @lru_cache(maxsize=128)  # 缓存常用查询
    def get_date_scope(self, table, symbol_id='', date_field='date'):
        condition = f"WHERE variety='{symbol_id}'" if symbol_id else ""
        sql = f"SELECT MIN({date_field}), MAX({date_field}) FROM {table} {condition}"
        start_date, end_date = pd.read_sql_query(sql, self.conn).iloc[0]
        return start_date, end_date
    
    @lru_cache(maxsize=128)
    def get_variety_map(self):
        if self.variety_id_name_map is None or self.variety_name_id_map is None:
            sql = f"SELECT code, name FROM symbols"
            df = self.get_data_by_sql(sql)
            self.variety_id_name_map = df.set_index('code')['name'].to_dict()
            self.variety_name_id_map = df.set_index('name')['code'].to_dict()
        return self.variety_id_name_map, self.variety_name_id_map

    def update_data(self, table, updates, condition):
        """
        更新指定表中满足条件的记录。
        
        参数:
        - table: str, 数据表名
        - updates: dict, 字段及其更新值的字典
        - condition: str, 用于识别更新记录的条件
        
        返回:
        - int, 表示被更新的记录数
        """
        # 初始化 MetaData
        metadata = MetaData()
        # 使用autoload加载表结构
        table_ref = Table(table, metadata, autoload_with=self.engine)
        # 构建更新语句
        update_stmt = table_ref.update().where(text(condition)).values(**updates)
        # 执行更新操作并返回结果
        with self.engine.begin() as conn:
            result = conn.execute(update_stmt)
        # 清除相关缓存
        self.clear_cache()
        return result.rowcount  # 返回被更新的行数

    def delete_data(self, table, condition):
        """
        从指定表中删除满足条件的记录。

        参数:
        - table: str, 数据表名
        - condition: str, 用于识别要删除的记录的条件

        返回:
        - int, 表示被删除的记录数
        """
        # 初始化 MetaData
        metadata = MetaData()
        # 使用autoload加载表结构
        table_ref = Table(table, metadata, autoload_with=self.engine)
        # 构建删除语句
        delete_stmt = table_ref.delete().where(text(condition))
        # 执行删除操作并返回结果
        with self.engine.begin() as conn:
            result = conn.execute(delete_stmt)
        # 清除相关缓存
        self.clear_cache()
        return result.rowcount  # 返回被删除的行数

    def add_orm_data(self, orm_object):
        self.session.add(orm_object)
        self.session.commit()
    def get_orm_data(self, class_name,  **kwargs):
        result = self.session.query(class_name).filter_by(**kwargs).first()
        if result:
            return result
        else:
            raise ValueError(f"{class_name} with {kwargs} not found.")

    def query_orm_datas(self, class_name, **kwargs):
        results = self.session.query(class_name).filter_by(**kwargs).all()
        if results:
            return results
        else:
            raise ValueError(f"{class_name} with {kwargs} not found.")

    def update_orm_data(self, class_name, id, **kwargs):
        result = self.session.query(class_name).filter_by(id=id).first()
        if result:
            for key, value in kwargs.items():
                setattr(result, key, value)
            self.session.commit()
        else:
            raise ValueError(f"{class_name} with id {id} not found.")
    
    def delete_orm_data(self, class_name, id):
        result = self.session.query(class_name).filter_by(id=id).first()
        if result:
            self.session.delete(result)
            self.session.commit()
        else:
            raise ValueError(f"{class_name} with id {id} not found.")
    
    def clear_cache(self):
        """
        清除所有缓存的查询结果，以确保数据的一致性。
        """
        self.get_data.cache_clear()
        self.get_data_by_sql.cache_clear()
        self.get_data_by_symbol.cache_clear()

    def get_variety_setting(self, json_file=''):
        if self.variety_setting is None:
            if json_file!='':
                self.variety_json = json_file   
            self.variety_setting = self.load_json_setting(self.variety_json)
        return self.variety_setting
    
    def load_json_setting(self, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as setting_file:
                setting = json.load(setting_file)
        except IOError as e:
            setting = None
            print(f"Error reading configuration: {e}")        
        return setting
    
    def save_json_setting(self, json_file, setting):
        try:
            with open(json_file, 'w', encoding='utf-8') as setting_file:
                json.dump(setting, setting_file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def close(self):
        self.conn.close()
        self.engine.dispose()
