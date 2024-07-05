import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
import plotly.graph_objects as go
from dataworks import DataWorks

Base = declarative_base()

class ContractInfo(Base):
    __tablename__ = 'fees'
    
    交易所 = Column(String)                # 交易所
    合约 = Column(String, primary_key=True, unique=True)   # 合约
    合约名称 = Column(String)           # 合约名称
    品种 = Column(String)                 # 品种
    合约乘数 = Column(Float)               # 合约乘数
    开仓费率 = Column(Float)            # 开仓费率
    每手开仓费 = Column(Float)        # 开仓费/手
    平仓费率 = Column(Float)           # 平仓费率
    每手平仓费 = Column(Float)       # 平仓费/手
    平今仓费率 = Column(Float)     # 平今仓费率
    每手平今仓费 = Column(Float) # 平今仓费/手
    # 上日结算价 = Column(Float)    # 上日结算价
    # 成交量 = Column(Integer)                 # 成交量
    # 空盘量 = Column(Integer)          # 空盘量
    每手开仓手续费 = Column(Float)        # 1手开仓手续费
    每手平仓手续费 = Column(Float)       # 1手平仓手续费
    每手平今仓手续费 = Column(Float) # 1手平今仓手续费
    做多保证金率 = Column(Float)         # 做多保证金率
    每手做多保证金 = Column(Float)     # 做多保证金/手
    做空保证金率 = Column(Float)        # 做空保证金率
    每手做空保证金 = Column(Float)    # 做空保证金/手
    做多每手保证金 = Column(Float)     # 做多1手保证金
    做空每手保证金 = Column(Float)    # 做空1手保证金
    最小变动价位 = Column(Float)       # 最小变动价位
    每Tick盈亏 = Column(Float)             # 1Tick盈亏

class TradingPlan(Base):
    __tablename__ = 'trading_plan'
    id = Column(Integer, primary_key=True)
    contract = Column(String)
    direction = Column(Enum('LONG', 'SHORT'))
    entry_price = Column(Float)
    take_profit_price = Column(Float)
    stop_loss_price = Column(Float)
    position_size = Column(Float)
    risk_reward_ratio = Column(Float)
    expected_profit = Column(Float)
    expected_loss = Column(Float)

class TradeExecution(Base):
    __tablename__ = 'trade_execution'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer)
    batch = Column(Integer)
    date = Column(DateTime)
    entry_price = Column(Float)
    exit_price = Column(Float)
    position_size = Column(Float)
    pnl = Column(Float)

class TradingPlanManager:
    def __init__(self, db_url, initial_capital, max_loss_ratio):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.initial_capital = initial_capital
        self.max_loss_ratio = max_loss_ratio

    def get_contract_info(self, contract):
        with DataWorks() as dws:
            contract_info = dws.get_orm_data(ContractInfo, contract)
        return contract_info

    def calculate_position(self, contract, entry_price, stop_loss_price):
        with DataWorks() as dws:
            contract_info = dws.get_orm_data(ContractInfo, contract)
        max_loss_amount = self.initial_capital * self.max_loss_ratio
        point_value = contract_info.合约乘数
        stop_loss_points = abs(entry_price - stop_loss_price)
        position_size = max_loss_amount / (stop_loss_points * point_value)
        return position_size

    def add_trading_plan(self, contract, direction, entry_price, take_profit_price, stop_loss_price):
        with DataWorks() as dws:
            contract_info = dws.get_orm_data(ContractInfo, contract)
        point_value = contract_info.合约乘数
        position_size = self.calculate_position(contract, entry_price, stop_loss_price)
        risk_reward_ratio = abs(take_profit_price - entry_price) / abs(entry_price - stop_loss_price)
        expected_profit = (take_profit_price - entry_price) * position_size * point_value
        expected_loss = (entry_price - stop_loss_price) * position_size * point_value
        new_plan = TradingPlan(contract=contract, direction=direction, entry_price=entry_price,
                               take_profit_price=take_profit_price, stop_loss_price=stop_loss_price,
                               position_size=position_size, risk_reward_ratio=risk_reward_ratio,
                               expected_profit=expected_profit, expected_loss=expected_loss)
        self.session.add(new_plan)
        self.session.commit()
    
    def update_trading_plan(self, plan_id, **kwargs):
        with DataWorks() as dws:
            dws.update_orm_data(TradingPlan, plan_id, **kwargs)

    def delete_trading_plan(self, plan_id):
        with DataWorks() as dws:
            dws.delete_orm_data(TradingPlan, plan_id)

    def query_trading_plan(self, plan_id):
        with DataWorks() as dws:
            plan = dws.get_orm_data(TradingPlan, plan_id)
        return plan

    def execute_trade(self, plan_id, batch, date, entry_price, exit_price, position_size):
        pnl = (exit_price - entry_price) * position_size * self.get_contract_info(self.query_trading_plan(plan_id).contract).multiplier
        new_execution = TradeExecution(plan_id=plan_id, batch=batch, date=date, entry_price=entry_price, exit_price=exit_price, position_size=position_size, pnl=pnl)
        with DataWorks() as dws:
            dws.add_orm_data(new_execution)

    def plot_trading_plan(self, plan_id):
        with DataWorks() as dws:
            executions = dws.query_orm_datas(TradeExecution, plan_id)
        
        entry_prices = [execution.entry_price for execution in executions]
        exit_prices = [execution.exit_price for execution in executions]
        dates = [execution.date for execution in executions]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=entry_prices, mode='lines+markers', name='Entry Prices'))
        fig.add_trace(go.Scatter(x=dates, y=exit_prices, mode='lines+markers', name='Exit Prices'))
        fig.update_layout(title='Trading Plan Execution', xaxis_title='Date', yaxis_title='Price')
        fig.show()
