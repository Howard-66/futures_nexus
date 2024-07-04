import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import plotly.graph_objects as go

Base = declarative_base()

class ContractInfo(Base):
    __tablename__ = 'contract_info'
    id = Column(Integer, primary_key=True)
    contract = Column(String, unique=True)
    multiplier = Column(Float)
    margin_rate = Column(Float)
    fee = Column(Float)

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
        return self.session.query(ContractInfo).filter_by(contract=contract).first()

    def calculate_position(self, contract, entry_price, stop_loss_price):
        contract_info = self.get_contract_info(contract)
        max_loss_amount = self.initial_capital * self.max_loss_ratio
        point_value = contract_info.multiplier
        stop_loss_points = abs(entry_price - stop_loss_price)
        position_size = max_loss_amount / (stop_loss_points * point_value)
        return position_size

    def add_trading_plan(self, contract, direction, entry_price, take_profit_price, stop_loss_price):
        position_size = self.calculate_position(contract, entry_price, stop_loss_price)
        risk_reward_ratio = abs(take_profit_price - entry_price) / abs(entry_price - stop_loss_price)
        expected_profit = (take_profit_price - entry_price) * position_size * self.get_contract_info(contract).multiplier
        expected_loss = (entry_price - stop_loss_price) * position_size * self.get_contract_info(contract).multiplier
        new_plan = TradingPlan(contract=contract, direction=direction, entry_price=entry_price,
                               take_profit_price=take_profit_price, stop_loss_price=stop_loss_price,
                               position_size=position_size, risk_reward_ratio=risk_reward_ratio,
                               expected_profit=expected_profit, expected_loss=expected_loss)
        self.session.add(new_plan)
        self.session.commit()
    
    def update_trading_plan(self, plan_id, **kwargs):
        plan = self.session.query(TradingPlan).filter_by(id=plan_id).first()
        for key, value in kwargs.items():
            setattr(plan, key, value)
        self.session.commit()
    
    def delete_trading_plan(self, plan_id):
        plan = self.session.query(TradingPlan).filter_by(id=plan_id).first()
        self.session.delete(plan)
        self.session.commit()

    def query_trading_plan(self, plan_id):
        return self.session.query(TradingPlan).filter_by(id=plan_id).first()

    def execute_trade(self, plan_id, batch, date, entry_price, exit_price, position_size):
        pnl = (exit_price - entry_price) * position_size * self.get_contract_info(self.query_trading_plan(plan_id).contract).multiplier
        new_execution = TradeExecution(plan_id=plan_id, batch=batch, date=date, entry_price=entry_price, exit_price=exit_price, position_size=position_size, pnl=pnl)
        self.session.add(new_execution)
        self.session.commit()

    def plot_trading_plan(self, plan_id):
        plan = self.query_trading_plan(plan_id)
        executions = self.session.query(TradeExecution).filter_by(plan_id=plan_id).all()
        
        entry_prices = [execution.entry_price for execution in executions]
        exit_prices = [execution.exit_price for execution in executions]
        dates = [execution.date for execution in executions]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=entry_prices, mode='lines+markers', name='Entry Prices'))
        fig.add_trace(go.Scatter(x=dates, y=exit_prices, mode='lines+markers', name='Exit Prices'))
        fig.update_layout(title='Trading Plan Execution', xaxis_title='Date', yaxis_title='Price')
        fig.show()
