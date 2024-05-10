import pandas as pd
import sqlite3
import re
from asteval import Interpreter

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
        columns = source['columns']
        formula = None
        if isinstance(columns, str):  # 如果是字符串公式，解析出涉及的列名
            formula = columns              
            columns = self._parse_columns_from_formula(columns)           
        # columns = [re.sub(r'[0-9:]', '', col) for col in columns]          
        source['columns'] = columns if 'date' in columns else ['date'] + columns

        # 从数据源加载数据
        data = self._load_data(source)
        # for col in columns:
        #     # 尝试将每一列转换为数值类型
        #     data[col] = pd.to_numeric(data[col])
        # 排除 datetime 类型的列，对其余列应用 pd.to_numeric
        data[data.select_dtypes(exclude=['datetime']).columns] = data.select_dtypes(exclude=['datetime']).apply(pd.to_numeric)

        
        # 如果有转换函数，对数据进行转换
        if source['transform']:
            data = self._transform_data(data, source['transform'], columns)
        # 如果原始列定义是公式
        if formula and len(columns)>1:  
            data = self._calculate_formula(data, name, formula, columns)
        # 将处理后的数据缓存起来
        self.cache[name] = data

        return data

    def _load_data(self, source):
        """
        根据提供的数据源信息从SQLite数据库/ChoiceExcel文件中加载数据。
        """
        if source['source_type'] == 'SQLite':
            return self._load_data_from_sqlite(source['path'], source['table'], source['variety'], source['columns'])
        elif source['source_type'] == 'ChoiceExcel':
            return self._load_data_from_excel(source['path'], source['columns'])
        else:
            raise ValueError("Unsupported data source type")

    def _load_data_from_sqlite(self, path, table, variety, columns):
        """
        从SQLite数据库中加载数据。
        """
        conn = sqlite3.connect(path)
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if variety:
            query += f" WHERE variety = '{variety}'"
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data

    def _load_data_from_excel(self, path, columns):
        """
        从ChoiceExcel文件中加载数据。
        """
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
        """
        根据提供的转换函数对数据进行转换。
        
        参数:
        - data: 要转换的数据。
        - how: 转换函数的名称。
        - on: 要转换的列名。
        
        返回值:
        - 转换后的数据。
        """
        if how == 'Fill_Forward':
            data[on] = data[on].ffill().infer_objects()
        elif how == 'Fill_Backward':
            data[on] = data[on].bfill().infer_objects()
        return data

    def _parse_columns_from_formula(self, formula):
        """
        从公式中解析出涉及的列名。
        
        参数:
        - formula: 要解析的公式。
        
        返回值:
        - 提取出的列名列表。
        """
        # 这里需要一个解析器来从公式中提取列名
        # 示例实现，实际实现应更全面地处理字符串中的列名
        return re.findall(r'\w[\w:()%]*', formula)  # 假设列名是单词字符
    
    def _calculate_formula(self, data, name, formula, columns):     
        """
        根据提供的公式对数据进行计算。
        
        参数:
        - data: 要计算数据的数据框。
        - name: 计算结果要保存的列名。
        - formula: 要计算的公式。
        - columns: 要计算公式的列名。
        
        返回值:
        - 计算后的数据。
        """              
        aeval = Interpreter() 
        for col in columns:                    
            safe_col = re.sub(r'[0-9:]', '', col)
            data.rename(columns={col:safe_col}, inplace=True)
            aeval.symtable[safe_col] = data[safe_col]
        formula = re.sub(r'[0-9:]', '', formula)
        data[name] = aeval.eval(formula)
        return data
