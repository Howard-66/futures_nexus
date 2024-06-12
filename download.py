import pandas as pd
import akshare as ak
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
import dataworks as dw
import json

dws = dw.DataWorks()

# 获取历史合约

# 获取DCE合约
def get_dce_contract():
    last_date = dws.get_last_date('dce')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)
    df_futures_daily_dce_append = ak.get_futures_daily(start_date=start_date, end_date=end_date, market="DCE")
    df_futures_daily_dce_append['date'] = pd.to_datetime(df_futures_daily_dce_append['date'], format='%Y%m%d')
    dws.save_data(df_futures_daily_dce_append, 'dce', 'append')

# 获取CZCE合约
def get_czce_contract():
    last_date = dws.get_last_date('dce')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)
    df_futures_daily_dce_append = ak.get_futures_daily(start_date=start_date, end_date=end_date, market="DCE")
    df_futures_daily_dce_append['date'] = pd.to_datetime(df_futures_daily_dce_append['date'], format='%Y%m%d')
    dws.save_data(df_futures_daily_dce_append, 'dce', 'append')

# 获取SHFE合约
def get_shfe_contract():
    last_date = dws.get_last_date('shfe')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)
    df_futures_daily_shfe_append = ak.get_futures_daily(start_date=start_date, end_date=end_date, market="SHFE")
    df_futures_daily_shfe_append['date'] = pd.to_datetime(df_futures_daily_shfe_append['date'], format='%Y%m%d')
    df_futures_daily_shfe_append = df_futures_daily_shfe_append.drop('index', axis=1)
    dws.save_data(df_futures_daily_shfe_append, 'shfe', 'append')

# 获取合约信息
def get_contract_info():
    symbol_list = ak.futures_index_symbol_table_nh()
    symbol_list = symbol_list[symbol_list['exchange'].isin(['郑州商品交易所', '大连商品交易所', '上海期货交易所'])]
    symbol_list = symbol_list.drop('indexcategory', axis=1)
    exchange_replace_dict = {'郑州商品交易所': 'czce',
                            '大连商品交易所': 'dce',
                            '上海期货交易所': 'shfe'}
    symbol_list['exchange'] = symbol_list['exchange'].apply(lambda x: exchange_replace_dict.get(x, x))
    dws.save_data(symbol_list, 'symbols')

# 获取主力合约
def get_main_contract():
    contract_list = ak.futures_display_main_sina()
    contract_list = contract_list[contract_list['exchange'].isin(['czce', 'dce', 'shfe'])]

    last_date = dws.get_last_date('dominant')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)
    main_contract_data = []
    for symbol in contract_list['symbol']:
        symbol_hist = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)
        symbol_hist['variety'] = symbol
        main_contract_data.append(symbol_hist)
    merged_main_contracts = pd.concat(main_contract_data)
    merged_main_contracts.rename(columns={'日期': 'date'}, inplace=True)
    merged_main_contracts['date'] = pd.to_datetime(merged_main_contracts['date'])
    merged_main_contracts['variety'] = merged_main_contracts['variety'].str.rstrip('0')
    # combined_main = merged_main_contracts.drop_duplicates(subset=['日期', 'variety'], keep='last')
    dws.save_data(merged_main_contracts, 'dominant', 'append')

# 合成近月合约
def get_near_contract():
    import re
    variety_setting = dws.get_variety_setting()
    ignore_variety = ['SC_TAS']
    df_near_contract = pd.DataFrame()
    for variety in variety_setting:
        dominant_months = variety_setting[variety]['DominantMonths']
        exchange = variety_setting[variety]['ExchangeID']
        df_history_variety = dws.get_data_by_symbol(exchange, variety)
        df_history_variety['delivery_month'] = df_history_variety['symbol'].str.slice(-2).astype(int)
        print(variety, exchange)
        df_history_variety['date'] = pd.to_datetime(df_history_variety['date'], format='ISO8601')
        df_dominant_contract = df_history_variety[df_history_variety['delivery_month'].isin(dominant_months)]
        df_dominant_contract = df_dominant_contract.sort_values(by=['date'], ascending=[True])
        contract_list = df_dominant_contract['symbol'].unique()
        first_symbol = True
        for symbol in contract_list:
            number_count = len(re.findall(r'\d', symbol))
            df_cuurent_near = df_dominant_contract[df_dominant_contract['symbol']==symbol]
            if first_symbol:
                first_symbol = False
                start_date = df_cuurent_near['date'].min()        
            if number_count==4:    
                # 假设年月编码是symbol字符串的后四位
                year_month_code = symbol[-4:]
                year = int(year_month_code[:2])  # 提取年份编码
                month = int(year_month_code[2:])  # 提取月份编码
                year += 2000 if year < 50 else 1900
                delivery_date = datetime(year, month, 1)
            else:
                # TODO: 合约编码3位数字的品种处理逻辑
                year_month_code = symbol[-3:]
                # year = int(year_month_code[:1])  # 提取年份编码
                month = int(year_month_code[1:])  # 提取月份编码
                delivery_date = df_cuurent_near['date'].max()    
                delivery_date = delivery_date.replace(month=month, day=1)
                # year += 2020
            end_date = delivery_date - timedelta(days=1)    
            if start_date > end_date:
                continue        
            df_cuurent_near = df_cuurent_near[(df_cuurent_near['date']>= start_date) & (df_cuurent_near['date']<=end_date)]
            df_near_contract = pd.concat([df_near_contract, df_cuurent_near])
            start_date = end_date + timedelta(days=1)            
    dws.save_data(df_near_contract, 'near') 

# 获取注册仓单
def get_receipt():
    last_date = dws.get_last_date('receipt')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)    

    dce =  ['C', 'CS', 'A', 'B', 'M', 'Y', 'P', 'FB', 'BB', 'JD', 'L', 'V', 'PP', 'J', 'JM', 'I', 'EG', 'RR', 'EB', 'PG', 'LH'] 
    dce_in = ['A', 'M', 'C', 'Y', 'L', 'P', 'V', 'J', 'JM', 'I', 'JD', 'BB', 'FB', 'PP', 'CS', 'EG', 'RR', 'B', 'EB']
    czce = ['WH', 'PM', 'CF', 'SR', 'TA', 'OI', 'RI', 'MA', 'ME', 'FG', 'RS', 'RM', 'ZC', 'JR', 'LR', 'SF', 'SM', 'WT', 'TC', 'GN', 'RO', 'ER', 'SRX', 'SRY', 'WSX', 'WSY', 'CY', 'AP', 'UR', 'CJ', 'SA', 'PK', 'PF', 'PX', 'SH'] 
    czce_in = ['CF', 'SR', 'TA', 'PM', 'RO', 'ER', 'FG', 'RS', 'RM', 'JR', 'LR', 'SM', 'SF', 'ME', 'TC', 'CY', 'AP', 'CJ', 'UR', 'SA']
    shfe = ['CU', 'AL', 'ZN', 'PB', 'NI', 'SN', 'AU', 'AG', 'RB', 'WR', 'HC', 'FU', 'BU', 'RU', 'SC', 'NR', 'SP', 'SS', 'LU', 'BC', 'AO', 'BR', 'EC']

    # DCE
    df_receipt_dce_append = ak.get_receipt(start_date, end_date, vars_list=dce)
    df_receipt_dce_append['date'] = pd.to_datetime(df_receipt_dce_append['date'])
    df_receipt_dce_append.rename(columns={'var': 'variety'}, inplace=True)
    dws.save_data(df_receipt_dce_append, 'receipt', 'append')

    # CZCE
    df_receipt_czce_append = ak.get_receipt(start_date, end_date, vars_list=czce)
    df_receipt_czce_append['date'] = pd.to_datetime(df_receipt_czce_append['date'])
    df_receipt_czce_append.rename(columns={'var': 'variety'}, inplace=True)
    dws.save_data(df_receipt_czce_append, 'receipt', 'append')

    # SHFE
    df_receipt_shfe_append = ak.get_receipt(start_date, end_date, vars_list=shfe)
    df_receipt_shfe_append['date'] = pd.to_datetime(df_receipt_shfe_append['date'])
    df_receipt_shfe_append.rename(columns={'var': 'variety'}, inplace=True)
    dws.save_data(df_receipt_shfe_append, 'receipt', 'append')

    # 按日期/品种去重
    receipt_data = dws.get_data_by_sql('SELECT * FROM receipt')
    receipt_data['date'] = pd.to_datetime(receipt_data['date'], format='ISO8601')
    receipt_data_drop_dup = receipt_data.drop_duplicates(subset=['date', 'variety'], keep='last')
    dws.save_data(receipt_data_drop_dup, 'receipt')

# 获取基差
def get_basis():
    last_date = dws.get_last_date('basis')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    delta = timedelta(days=1)
    dates = []
    while start_date <= end_date:
        dates.append(start_date.strftime("%Y%m%d"))
        start_date += delta
    all_data = pd.DataFrame()
    for d in dates:
        df = ak.futures_spot_price(d)
        all_data = pd.concat([all_data, df], ignore_index=True)
    all_data['date'] = pd.to_datetime(all_data['date'])
    all_data.rename(columns={'symbol': 'variety'}, inplace=True)
    # 纠正AKShare基差/基差率计算错误（正负号）
    all_data['near_basis'] = -all_data['near_basis']
    all_data['dom_basis'] = -all_data['dom_basis']
    all_data['near_basis_rate'] = -all_data['near_basis_rate']
    all_data['dom_basis_rate'] = -all_data['dom_basis_rate']
    dws.save_data(all_data, 'basis', 'append')

# 合成期限结构(全量)
def get_term_structure_all():
    last_date = dws.get_last_date('term_structure')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    print('Current Period: ', start_date, end_date)

    df_term_structure = pd.DataFrame(columns=['variety', 'date', 'flag', 'exchange'])

    variety_json = 'setting/variety.json'        
    with open(variety_json, encoding='utf-8') as variety_file:
        variety_setting = json.load(variety_file)

    df_term = dws.get_data_by_sql(f"SELECT * FROM dominant")
    dominant_list = df_term['variety'].unique()

    # TODO: 增加贵金属交易所
    exchange_list = ['czce', 'dce', 'shfe']
    for exchange_id in exchange_list:
        df_term = dws.get_data_by_sql(f"SELECT * FROM {exchange_id}")
        df_term['date'] = pd.to_datetime(df_term['date'])
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        variety_list = df_term['variety'].unique()
        variety_list = set(dominant_list) & set(variety_list)
        for variety_id in variety_list:
            print(f'{exchange_id}: {variety_id}')
            if variety_id not in variety_setting: continue
            dominant_months = variety_setting[variety_id]['DominantMonths']       
            df_variety = df_term[df_term['variety']==variety_id]
            date_list = df_variety['date'].unique()
            for trade_date in date_list:
                # print(trade_date)
                df_date = df_variety[df_variety['date']==trade_date]
                max_open_interest_index= df_date['open_interest'].idxmax()
                # domain_contract = df_date.loc[max_open_interest_index]['symbol']
                df_date = df_date.loc[max_open_interest_index:]                             
                df_dominant_contract = df_date[df_date['交割月'].isin(dominant_months)]
                if len(df_dominant_contract)<2:
                    trade_flag = 0
                else:
                    # print(df_dominant_contract)
                    diff = df_dominant_contract['settle'].head(len(dominant_months)+1).diff().dropna()
                    diff_trend = df_dominant_contract['settle'].iloc[-1] - df_dominant_contract['settle'].iloc[0]
                    trade_flag = -1 if all(diff>0) else 1 if all(diff<0) else -0.5 if diff_trend>0 else 0.5 if diff_trend<0 else 0 if diff_trend==0 else 0
                new_row = {'variety': variety_id,
                        'date': trade_date,
                        'flag': trade_flag,
                        'exchange': exchange_id}
                df_term_structure = pd.concat([df_term_structure, pd.DataFrame([new_row])], ignore_index=True)    
    df_term_structure['flag'] = df_term_structure['flag'].astype(float)
    dws.save_data(df_term_structure, 'term_structure')                

# 合成期限结构（增量）
def get_term_structure_period():
    # 获取最后一次数据生成的日期，转换为datetime对象，并确定下一个开始日期
    last_date = dws.get_last_date('term_structure')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)

    # 格式化日期用于查询或文件名
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    print('Current Period: ', start_date_str, end_date_str)

    # 准备存储期权结构数据的dataframe
    df_term_structure = pd.DataFrame(columns=['variety', 'date', 'flag', 'exchange'])

    # 加载品种设置
    variety_json = 'setting/variety.json'
    with open(variety_json, encoding='utf-8') as variety_file:
        variety_setting = json.load(variety_file)

    # 获取主导品种数据
    df_term = dws.get_data_by_sql(f"SELECT * FROM dominant WHERE date >= '{start_date_str}' AND date <= '{end_date_str}'")
    dominant_list = df_term['variety'].unique()

    # 在列表中包括额外的交易所
    exchange_list = ['czce', 'dce', 'shfe']  # 根据需要添加新的交易所

    # 遍历交易所和品种填充期权结构
    for exchange_id in exchange_list:
        df_term = dws.get_data_by_sql(f"SELECT * FROM {exchange_id} WHERE date >= '{start_date_str}' AND date <= '{end_date_str}'")
        df_term['date'] = pd.to_datetime(df_term['date'], format='ISO8601')
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        variety_list = df_term['variety'].unique()
        variety_list = set(dominant_list) & set(variety_list)

        for variety_id in variety_list:
            print(f'{exchange_id}: {variety_id}')
            if variety_id not in variety_setting:
                continue

            dominant_months = variety_setting[variety_id]['DominantMonths']
            df_variety = df_term[df_term['variety'] == variety_id]
            date_list = df_variety['date'].unique()

            for trade_date in date_list:
                df_date = df_variety[df_variety['date'] == trade_date]
                max_open_interest_index = df_date['open_interest'].idxmax()
                df_date = df_date.loc[max_open_interest_index:]
                df_dominant_contract = df_date[df_date['交割月'].isin(dominant_months)]

                if len(df_dominant_contract) < 2:
                    trade_flag = 0
                else:
                    diff = df_dominant_contract['settle'].head(len(dominant_months)+1).diff().dropna()
                    diff_trend = df_dominant_contract['settle'].iloc[-1] - df_dominant_contract['settle'].iloc[0]
                    trade_flag = -1 if all(diff > 0) else 1 if all(diff < 0) else -0.5 if diff_trend > 0 else 0.5 if diff_trend < 0 else 0 if diff_trend == 0 else 0

                new_row = {'variety': variety_id, 'date': trade_date, 'flag': trade_flag, 'exchange': exchange_id}
                df_term_structure = pd.concat([df_term_structure, pd.DataFrame([new_row])], ignore_index=True)

    # 根据需要保存或处理df_term_structure
    df_term_structure['flag'] = df_term_structure['flag'].astype(float)
    dws.save_data(df_term_structure, 'term_structure', 'append')

# 合成跨期价差（全量）
def get_term_spread_all():
    # last_date = dws.get_last_date('term_structure')
    # last_date = pd.to_datetime(last_date)
    # start_date = last_date + timedelta(days=1)
    # end_date = datetime.now() - timedelta(days=1)
    # start_date = start_date.strftime('%Y%m%d')
    # end_date = end_date.strftime('%Y%m%d')
    # print('Current Period: ', start_date, end_date)

    df_term_spread = pd.DataFrame(columns=['variety', 'date', 'primary_contract', 'primary_contract_close', 'secondary_contract', 'secondary_contract_close', 'spread', 'exchange'])

    variety_json = 'setting/variety.json'        
    with open(variety_json, encoding='utf-8') as variety_file:
        variety_setting = json.load(variety_file)

    df_term = dws.get_data_by_sql(f"SELECT * FROM dominant")
    dominant_list = df_term['variety'].unique()

    # TODO: 增加贵金属交易所
    exchange_list = ['czce', 'dce', 'shfe']
    for exchange_id in exchange_list:
        df_term = dws.get_data_by_sql(f"SELECT * FROM {exchange_id}")
        df_term['date'] = pd.to_datetime(df_term['date'])
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        variety_list = df_term['variety'].unique()
        variety_list = set(dominant_list) & set(variety_list)
        for variety_id in variety_list:
            print(f'{exchange_id}: {variety_id}')
            if variety_id not in variety_setting: continue
            dominant_months = variety_setting[variety_id]['DominantMonths']       
            # TODO: 如果主力合约月不大于2，使用非主力合约价差
            if len(dominant_months)<2: continue
            df_variety = df_term[df_term['variety']==variety_id]
            date_list = df_variety['date'].unique()
            for trade_date in date_list:
                # print(trade_date)
                df_date = df_variety[df_variety['date']==trade_date]
                max_open_interest_index= df_date['open_interest'].idxmax()
                # domain_contract = df_date.loc[max_open_interest_index]['symbol']
                df_date = df_date.loc[max_open_interest_index:]                             
                df_dominant_contract = df_date[df_date['交割月'].isin(dominant_months)]
                if len(df_dominant_contract)<2:           
                    continue
                else:
                    primary_contract = df_dominant_contract['symbol'].iloc[0]
                    primary_contract_close = df_dominant_contract['close'].iloc[0]
                    secondary_contract = df_dominant_contract['symbol'].iloc[1]
                    secondary_contract_close = df_dominant_contract['close'].iloc[1]              
                    spread = primary_contract_close - secondary_contract_close
                new_row = {'variety': variety_id,
                        'date': trade_date,
                        'primary_contract': primary_contract,
                        'primary_contract_close': primary_contract_close,                    
                        'secondary_contract': secondary_contract,
                        'secondary_contract_close': secondary_contract_close,
                        'spread': spread,
                        'exchange': exchange_id}
                df_term_spread = pd.concat([df_term_spread, pd.DataFrame([new_row])], ignore_index=True)
    dws.save_data(df_term_spread, 'spread', 'replace')

# 合成跨期价差（增量）
def get_term_spread_period():
    # 获取最后一次数据生成的日期，转换为datetime对象，并确定下一个开始日期
    last_date = dws.get_last_date('spread')
    last_date = pd.to_datetime(last_date)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)

    # 格式化日期用于查询或文件名
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    print('Current Period: ', start_date_str, end_date_str)

    df_term_spread = pd.DataFrame(columns=['variety', 'date', 'primary_contract', 'primary_contract_close', 'secondary_contract', 'secondary_contract_close', 'spread', 'exchange'])

    variety_json = 'setting/variety.json'        
    with open(variety_json, encoding='utf-8') as variety_file:
        variety_setting = json.load(variety_file)

    df_term = dws.get_data_by_sql(f"SELECT * FROM dominant WHERE date >= '{start_date_str}' AND date <= '{end_date_str}'")
    dominant_list = df_term['variety'].unique()

    # TODO: 增加贵金属交易所
    exchange_list = ['czce', 'dce', 'shfe']
    for exchange_id in exchange_list:
        df_term = dws.get_data_by_sql(f"SELECT * FROM {exchange_id} WHERE date >= '{start_date_str}' AND date <= '{end_date_str}'")
        df_term['date'] = pd.to_datetime(df_term['date'])
        df_term['交割月'] = df_term['symbol'].str.slice(-2).astype(int)
        variety_list = df_term['variety'].unique()
        variety_list = set(dominant_list) & set(variety_list)
        for variety_id in variety_list:
            print(f'{exchange_id}: {variety_id}')
            if variety_id not in variety_setting: continue
            dominant_months = variety_setting[variety_id]['DominantMonths']       
            # TODO: 如果主力合约月不大于2，使用非主力合约价差
            if len(dominant_months)<2: continue
            df_variety = df_term[df_term['variety']==variety_id]
            date_list = df_variety['date'].unique()
            for trade_date in date_list:
                # print(trade_date)
                df_date = df_variety[df_variety['date']==trade_date]
                max_open_interest_index= df_date['open_interest'].idxmax()
                # domain_contract = df_date.loc[max_open_interest_index]['symbol']
                df_date = df_date.loc[max_open_interest_index:]                             
                df_dominant_contract = df_date[df_date['交割月'].isin(dominant_months)]
                if len(df_dominant_contract)<2:           
                    continue
                else:
                    primary_contract = df_dominant_contract['symbol'].iloc[0]
                    primary_contract_close = df_dominant_contract['close'].iloc[0]
                    secondary_contract = df_dominant_contract['symbol'].iloc[1]
                    secondary_contract_close = df_dominant_contract['close'].iloc[1]              
                    spread = primary_contract_close - secondary_contract_close
                new_row = {'variety': variety_id,
                        'date': trade_date,
                        'primary_contract': primary_contract,
                        'primary_contract_close': primary_contract_close,                    
                        'secondary_contract': secondary_contract,
                        'secondary_contract_close': secondary_contract_close,
                        'spread': spread,
                        'exchange': exchange_id}
                df_term_spread = pd.concat([df_term_spread, pd.DataFrame([new_row])], ignore_index=True)    
    dws.save_data(df_term_spread, 'spread', 'append')

# Excel文件格式转换
import os
import pandas as pd

def convert_xlsx_to_csv(directory):
    # 遍历指定目录及其子目录下的所有文件
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.xlsx'):
                # 构建完整的文件路径
                xlsx_path = os.path.join(root, filename)
                # 构建对应的 csv 文件路径
                csv_filename = filename.replace('.xlsx', '.csv')
                csv_path = os.path.join(root, csv_filename)
                
                # 读取 xlsx 文件
                df = pd.read_excel(xlsx_path, engine='openpyxl')
                # 保存为 csv 文件
                df.to_csv(csv_path, index=False)
                print(f"Converted {xlsx_path} to {csv_path}")

download_config = {
    'get_dce_contract': '获取DCE合约',
    'get_czce_contract': '获取CZCE合约',
    'get_shfe_contract': '获取SHFE合约',
    # 'get_contract_info': '获取合约信息',
    'get_main_contract': '获取主力合约',
    'get_near_contract': '获取次主力合约',
    'get_receipt': '获取注册仓单',
    'get_basis': '获取基差数据',
    'get_term_structure_period': '获取跨期结构',
    'get_term_spread_period': '获取跨期价差'
}
def download():
    # 根据download_config中key的顺序执行函数
    for key in download_config.keys():
        if key in globals():
            str = download_config[key]
            print(f'{str}...')
            globals()[key]()

if __name__ == '__main__':
    download()
    print('Convert xlsx to csv...')
    convert_xlsx_to_csv('.')
    dws.close()