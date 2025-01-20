import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数


# 测试时间段，可根据数据时间更改
start_time = '20230701'
end_time = '20231231'

# 下方为股票代码，如使用指数数据，则请注释掉下方代码
df = pd.read_csv('chan/sh600000.csv', encoding='gbk', skiprows=1, parse_dates=['交易日期'])
# 复权函数
def rehabilitation(df):
    # =计算涨跌幅
    df['涨跌幅'] = df['收盘价'] / df['前收盘价'] - 1
    # =计算复权价：计算所有因子当中用到的价格，都使用复权价
    df['复权因子'] = (1 + df['涨跌幅']).cumprod()
    df['收盘价_复权'] = df['复权因子'] * (df.iloc[0]['收盘价'] / df.iloc[0]['复权因子'])
    df['开盘价_复权'] = df['开盘价'] / df['收盘价'] * df['收盘价_复权']
    df['最高价_复权'] = df['最高价'] / df['收盘价'] * df['收盘价_复权']
    df['最低价_复权'] = df['最低价'] / df['收盘价'] * df['收盘价_复权']
    # 原始的价格叫xx_原，复权两个字去掉
    df.rename(columns={'开盘价': '开盘价_原', '最高价': '最高价_原', '最低价': '最低价_原', '收盘价': '收盘价_原'}, inplace=True)
    df.rename(columns={'开盘价_复权': '开盘价', '最高价_复权': '最高价', '最低价_复权': '最低价', '收盘价_复权': '收盘价'}, inplace=True)
    return df
# 对股价进行复权
df = rehabilitation(df)
# 重命名一些关键列
df.rename(columns={'交易日期': 'candle_end_time', '最高价': 'high', '最低价': 'low'}, inplace=True)
# 保留股价的两位小数
df['high'] = df['high'].round(2)
df['low'] = df['low'].round(2)


# 下方为指数代码，如使用股票数据，请注释下行代码
# df = pd.read_csv('sh000001.csv', encoding='gbk', parse_dates=['candle_end_time'])

# 框定起始范围
df = df[df['candle_end_time'] >= pd.to_datetime(start_time)]
df = df[df['candle_end_time'] <= pd.to_datetime(end_time)]

# 确认每行数据的编号
df['line_no'] = range(len(df))
# 只保留关键数据
df = df[['candle_end_time', 'high', 'low', 'line_no']]

# 复制一个df
df2 = df.copy()

# 创建一个保留循环结果的results
results = {}

# 遍历每根 K 线，一根根向后去找包含关系并处理
for i in df['line_no']:
    df3 = df2[df2['line_no'] == i]
    print(i)

    if i not in results:
        results[i] = pd.DataFrame()  # 如果不存在，则创建一个空的 DataFrame
    # 获取上一次迭代的结果作为初始数据
    results1 = results[i]
    # 将上一次迭代的结果与新交易日的数据合并
    df1 = pd.concat([results1, df3], ignore_index=True)

    # # 确认包含关系的 K 线组，且标记为1的是后一根 K 线
    # 向前包含条件
    con1 = df1['low'] <= df1['low'].shift(1)
    con2 = df1['high'].shift(1) <= df1['high']
    # 向后包含条件
    con3 = df1['low'].shift(1) <= df1['low']
    con4 = df1['high'] <= df1['high'].shift(1)
    # 确认有包含关系的K线，标记为1
    df1.loc[(con1 & con2) | (con3 & con4), '包含关系'] = 1

    # 上升关系
    con5 = df1['high'].shift(2) < df1['high'].shift(1)
    con6 = df1['low'].shift(2) < df1['low'].shift(1)
    # 标记有上升关系的K线组
    df1.loc[con5 & con6, '位置关系'] = 1
    con7 = df1['位置关系'] == 1

    # 下降关系
    con8 = df1['high'].shift(2) > df1['high'].shift(1)
    con9 = df1['low'].shift(2) > df1['low'].shift(1)
    # 标记有下降关系的K线组
    df1.loc[con8 & con9, '位置关系'] = 0
    con10 = df1['位置关系'] == 0

    con11 = df1['包含关系'] == 1

    # 标记需要处理的K线位置，上升处理
    df1.loc[con7 & con11, '包含处理'] = 1
    # 标记需要处理的K线位置，下降处理
    df1.loc[con10 & con11, '包含处理'] = 0

    # 合成新K线
    mask = df1['包含处理'] == 1
    df1.loc[mask, 'high'] = np.maximum(df1['high'], df1['high'].shift(1))
    df1.loc[mask, 'low'] = np.maximum(df1['low'], df1['low'].shift(1))

    mask0 = df1['包含处理'] == 0
    df1.loc[mask0, 'high'] = np.minimum(df1['high'], df1['high'].shift(1))
    df1.loc[mask0, 'low'] = np.minimum(df1['low'], df1['low'].shift(1))

    print(df1['包含处理'].iloc[-1])

    # 删除已处理K线
    if df1['包含处理'].iloc[-1] in [1, 0]:
        print(df1.iloc[-2])
        # 删除倒数第二行，即已处理的K线
        df1.drop(df1.index[-2], axis=0, inplace=True)

    # 创建新的df_new来保存数据
    df_new = df1[['candle_end_time', 'high', 'low', 'line_no']]
    # 将数据保存进result，因下次调用i会加1，所以results[i+1]
    results[i+1] = df_new
    # 将最后一次遍历结果保存
    df_last = results[i+1]

print(df_last)
# 输出预处理K线的数据文件
df_last.to_csv('预处理 K 线-股票.csv', encoding='gbk')

# 选择画图的时间范围
df_last = df_last[df_last['candle_end_time'] >= pd.to_datetime(start_time)]
df_last = df_last[df_last['candle_end_time'] <= pd.to_datetime(end_time)]

# 创建图表
plt.figure(figsize=(14, 7), dpi=100)

# 绘制每个交易日的最低价到最高价的线
for index, row in df_last.iterrows():
    plt.plot([row['candle_end_time'], row['candle_end_time']], [row['low'], row['high']], color='black')

# 设置图表标题和轴标签
plt.title('Simplified K-Line Chart with Actual Dates')
plt.xlabel('Date')
plt.ylabel('Price')

# 设置日期格式化
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()  # Improve the x-date labels

plt.tight_layout()
plt.show()




