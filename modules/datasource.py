import pandas as pd
import sqlite3

class DataSourceManager:
    SQLITE_DB_PATH = 'data/futures.db'  # 定义SQLite数据库的常量路径
    def __init__(self):
        self.sources = {}
        self.cache = {}

    def add_data_source(self, name, source_type, path=None, table=None, variety=None, columns=None, transform=None):
        """
        向数据源列表中添加一个新的数据源。

        参数:
        name (str): 数据源的名称，用于唯一标识这个数据源。
        source_type (str): 数据源的类型，SQLite、ChoiceExcel、AKShare、Yfinance。
        path (str, 可选): 数据源的文件路径。如果未提供，则默认使用SQLite数据库的路径。
        table (str, 可选): 数据源中的表格名称。
        variety (str, 可选): 股票/商品品种。
        columns (list, 可选): 数据源中的列名列表。这可以帮助指定要处理的特定列。
        transform (function, 可选): 一个用于转换数据的函数。可以为数据应用这个函数以进行预处理。
        """
        # 在self.sources字典中添加新的数据源信息
        self.sources[name] = {
            "source_type": source_type,
            "path": path if path else self.SQLITE_DB_PATH,  # 如果提供了path则使用提供的path，否则使用默认的SQLite数据库路径
            "table": table,
            "variety": variety,
            "columns": columns,
            "transform": transform
        }

    def get_data(self, name):
        """
        根据提供的名称从数据源获取数据，并进行必要的转换。
        
        参数:
        - name: 数据源的名称，用于标识需要获取数据的来源。
        
        返回值:
        - 返回从指定数据源加载并转换后的数据。
        
        抛出:
        - ValueError: 如果指定的数据源不存在。
        """
        # 检查缓存中是否已有数据，如果有则直接返回
        if name in self.cache:
            return self.cache[name]

        # 如果数据源不存在于 sources 中，抛出 ValueError
        if name not in self.sources:
            raise ValueError("Data source not found")

        # 获取数据源信息，并确保 'date' 列存在于数据列中
        source = self.sources[name]
        key_cols = source['columns']
        source['columns'] = key_cols if 'date' in key_cols else ['date'] + key_cols

        # 从数据源加载数据
        data = self._load_data(source)
        for column in key_cols:
            # 尝试将每一列转换为数值类型
            data[column] = pd.to_numeric(data[column])
        
        # 如果有转换函数，对数据进行转换
        if source['transform']:
            data = self._transform_data(data, source['transform'], key_cols)
        
        # 将处理后的数据缓存起来
        self.cache[name] = data

        return data

    def _load_data(self, source):
        if source['source_type'] == 'SQLite':
            return self._load_data_from_sqlite(source['path'], source['table'], source['variety'], source['columns'])
        elif source['source_type'] == 'ChoiceExcel':
            return self._load_data_from_excel(source['path'], source['columns'])
        else:
            raise ValueError("Unsupported data source type")

    def _load_data_from_sqlite(self, path, table, variety, columns):
        conn = sqlite3.connect(path)
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if variety:
            query += f" WHERE variety = '{variety}'"
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data

    def _load_data_from_excel(self, path, columns):
        if not path:
            return None
        # 读取Excel文件，跳过前1行（假设第一行是“宏观数据”等标题，不是列名称）
        df = pd.read_excel(path, header=1)  # 利用header=1使得第2行（即索引1）作为列标题
        # 数据有效行从第7行开始，即需要跳过第2-6行（索引从0开始，所以是1-5）
        df = df[5:]  # 从第6行开始保留数据（因为header=1后，第二行已经变成了索引0）
        # 将第1列的名称改为'date'
        df.rename(columns={df.columns[0]: 'date'}, inplace=True)
        # 剔除日期列为空的行以及日期列为“数据来源：东方财富Choice数据”的行
        df = df[df['date'].notna() & (df['date'] != '数据来源：东方财富Choice数据')]
        # 将日期列转换为datetime类型
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # 再次剔除转换错误后可能产生的NaT值
        df = df[df['date'].notna()]
        # 仅保留所需的列
        df = df[columns]
        return df
    
    def _transform_data(self, data, how, on):
        if how == 'Fill_Forward':
            data[on] = data[on].ffill().infer_objects()
        elif how == 'Fill_Backward':
            data[on] = data[on].bfill().infer_objects()
        return data

    def _calculate_data(self, data, func):
        return data
