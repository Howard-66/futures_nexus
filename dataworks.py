import pandas as pd
import sqlite3
import json

class DataWorks:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('futures_nexus/data/futures.db')
        self.variety_setting = None
        self.variety_json = 'setting/variety.json'
        self.variety_id_name_map = None
        self.variety_name_id_map = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_data_by_sql(self, sql):
        self.conn = sqlite3.connect('data/futures.db')
        return pd.read_sql_query(sql, self.conn)
    
    def get_data(self, table, condition, fields='*'):
        # self.conn = sqlite3.connect('data/futures.db')
        # cursor = self.conn.cursor()
        if fields=='*':
            fields_str = fields
        elif isinstance(fields, str):
            fields_str = fields
        else:
            fields_str = ', '.join(fields)  # Convert the list of fields into a comma-separated string
        sql = f"SELECT {fields_str} FROM {table} WHERE {condition}"
        # cursor.execute(sql)
        # data = cursor.fetchall()
        df = pd.read_sql_query(sql, self.conn)
        # cursor.close()
        # self.conn.close()
        return df
    
    def get_data_by_symbol(self, table, symbol_id, fields='*'):
        condition = f"variety='{symbol_id}'"
        df = self.get_data(table, condition, fields)
        # df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_from_dataframe(self, df, to_table, mode='replace'):
        df.to_sql(to_table, self.conn, if_exists=mode, index=False)

    def get_last_date(self, table, symbol_id='', date_field='date'):
        if symbol_id:
            condition = f"{date_field} IN (SELECT MAX({date_field}) FROM {table} WHERE variety='{symbol_id}')"
        else:
            condition = f"{date_field} IN (SELECT MAX({date_field}) FROM {table})"
        sql = f"SELECT {date_field} FROM {table} WHERE {condition}"
        last_date = pd.read_sql_query(sql, self.conn).iloc[0][date_field]
        return last_date
    
    def get_date_scope(self, table, symbol_id='', date_field='date'):
        if symbol_id:
            condition = f"WHERE variety='{symbol_id}'"
        else:
            condition = ""
        sql = f"SELECT MIN({date_field}), MAX({date_field}) FROM {table} {condition}"
        start_date, end_date = pd.read_sql_query(sql, self.conn).iloc[0]
        return start_date, end_date
    
    def get_variety_map(self):
        if self.variety_id_name_map is None or self.variety_name_id_map is None:
            sql = f"SELECT code, name FROM symbols"
            df = pd.read_sql_query(sql, self.conn)
            self.variety_id_name_map = df.set_index('code')['name'].to_dict()
            self.variety_name_id_map = df.set_index('name')['code'].to_dict()
        return self.variety_id_name_map, self.variety_name_id_map

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