import pandas as pd
import sqlite3

class DataWorks:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('data/futures.db')
        # self.conn = None

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
    
    def get_data_by_symbol(self, table, fields, symbol_id):
        condition = f"variety='{symbol_id}'"
        df = self.get_data(table, condition, fields)
        # df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_from_dataframe(self, df, to_table, mode='replace'):
        df.to_sql(to_table, self.conn, if_exists=mode, index=False)

    def close(self):
        self.conn.close()