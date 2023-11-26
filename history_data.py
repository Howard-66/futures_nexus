import pandas as pd

def load_choice_file(file_path):
    # 读取Choice导出的数据文件并按照约定规则格式化
    # 处理规则：
    # 1、数据的第一行作为指标标题
    # 2、第一列作为日期
    # 3、前四行和最后一行都不是数据内容
    # 4、中间可能存在空行
    df = pd.read_excel(file_path)
    df.columns = df.iloc[0]
    df.rename(columns={df.columns[0]: '日期'}, inplace=True)
    df = df[4:-1]
    df.reset_index(drop=True, inplace=True)
    df.dropna(axis=0, subset=['日期'], inplace=True)
    return df