TODO:

- 整体布局
    - 使用Multi-Page模式设计页面路由（done）
    - 使用Dash Mantine Component组建设计页面布局（done）
    - 头部主菜单设计（done）
    - 侧边栏菜单设计（分析步骤/板块品种/自选品种）（done）
    - 使用标签切换分析窗口(done)
    - 支持颜色主题（done）
    - 品种搜索功能（done）
    - 自选品种列表（done）
    - 交易页面设计
- 数据/指标计算
    - 期限结构指标(done)
    - 根据类型为指标配色([-1,1](NP1), 历史分位，[]0,1]，后缀P表示正值红色显示，NP1表示负值红色显示)(done)
    - 实现可配置的利润计算公式(done)
    - 跨期价差数据（done）
    - 重新设计指标管理和绘制类(done)
    - 跨月价差+周期性分析作为辅图指标(done)
    - 主成分分析/智能指标选择
    - 宏观数据
    - 国际商品数据
    - 关联股票数据
    - 同比指标
    - 合约调仓/展期收益率
    - 交割数据（虚实比、期转现）
    - 利润数据/利润期限结构
    - 重新优化信号计算和显示
    - 数据合并、指标计算等函数优化为并行运算
- 图表优化
    - 基本面分析主图（基差-库存-利润分析图表）（done）
    - 基本面分析主图指标配置（done）
    - 标记现货月时间（done）
    - 期货合约类型选择（主力合约/近月合约）（done）
    - 指标的多空标签（done）
    - 联动显示期限结构趋势（done）
    - 联动显示跨期套利图表（done）
    - 利润-风险测算表格（done）
    - 根据品种的数据源，绘制指标（包含基差率、持仓量）(done)
    - 重新设计基本面分析页面的指标配置工具条(done)
    - 期限结构分析中去掉与现货的比较(done)
    - 保存用户指标选择(done)
    - 指标/坐标轴/图例样式优化(done)
    - 图表配色优化(done)    
    - 将量化分析标签、盈利风险测算拆分为不同的Card(done)
    - 根据每一个子图表的可视数据范围设置初始坐标轴（done）
    - 移动图表时，更新每一个子图表坐标轴
    - 根据用户选择加载指标
    - 优化图表的加载速度(done)
    - 限制最大加载数据的数量(done)
    - 期限结构颜色按照指标配色显示，绘制一年内所有合约点(done)
    - 移动图表时，分段加载更早的数据
    - 动态更新打开品种的数据源 **
    - 指标组合关系使用提示（库存/仓单，开工率/产能利用率）
    - 单一图表调整为px对象
    - 使用Patch对象优化图表的局部更新
    - 标记主力合约更替 ***
    - 复盘模式
- 技术分析
    - K线图
    - MACD指标
    - RSI指标
    - BOLL指标
    - 均线指标
    - 画线：斐波那契回撤
    - 画线：斐波那契扩展
    - 画线：趋势线
    - 画线：多头/空头
- 季节性分析/周期性分析
    - 基本面指标支持季节分析(done)
    - 现货价格季节图/年度-月度涨跌统计矩阵 **
    - 期货主力合约季节图（可选主力合约）
    - 基差率季节图/年度-月度涨跌统计矩阵/频率分布统计
    - 仓单季节图/年度-月度涨跌统计矩阵
    - 库存季节图/年度-月度涨跌统计矩阵
    - 利润季节图/年度-月度涨跌统计矩阵
    - 趋势-周期-残差分析 **
    - ACF/PACF分析
    - 频域分析
    - 使用ARIMA、SARIMA建模、验证和预测
    - 周期性图表AI读图
- 套利分析
    - 跨期价差分析-多期排列/季节图/年度-月度涨跌统计矩阵 **
    - 基差-月差分析
    - 跨品种价差/价比分析-多期排列/季节图/年度-月度涨跌统计矩阵（自由品种比较/常见组合比较，可选择主力合约）
- 库存分析
    库存周期
    交割分析（虚实比、期转现）
- 产业链分析
    - 产业链/板块品种加载 **
    - 板块品种热力图（持仓量/市值）
    - 产业链经济数据是图
    - 基差概览
    - 期限结构概览
    - 四象限模型
    - 供需关系：成本/利润，生产/消费，产业链库存/利润，区分上中下游，及其相互关系
- 市场全景
    - 热力图（持仓量/交易量）(done)
    - 品种页面快速访问（done）
    - 侧边栏菜单
    - 基差概览
    - 期限结构概览    
    - 四象限模型    
- 加强学习分析
    - 单品种回测视图
    - 投资组合回测视图
    - AI投资建议
    - AI价格预测
- 技术分析
    - 常用技术指标（MACD、RSI）
    - 缠论信号提示（分形、笔/线段/中枢，各类买卖点）
- 交易计划
    - 分析记录/日志管理（移到工具栏）***
    - 投资组合管理/套利交易对管理
    - 交易计划和执行日志
- 配置管理
    - 数据索引/关联品种/公式配置
    - 实现自选品种管理 ***
    - 数据配置/数据源管理
    - 数据下载

Bugfix:
- 解决RB基差数据outlier的问题(done)
- 点击主图时，副图指标对应日期数据缺失，引发异常
- 品种关键数据有零或其他异常值（期货价格-结算价）
- 盈利-风险测算时，部分情况下点差计算错误
- 统一解决2023-8-28日起主力合约结算价为0的问题
- 基差/期限结构（预运算/副图计算）/跨期分析/跨月价差按照统一的价格类型（结算价/收盘价）计算
- 部分数据的历史分位计算结果为NaN，导致绘图颜色为黑色、点击鼠标后异常
- 焦炭的品种DataIndex配置中补充基差/基差率数据

-------------------
周期性分析：
    如何使用Python中的statsmodels库来实现ARIMA模型？
    在进行时间序列分析时，如何确定最佳的季节性周期？
    如果时间序列数据存在异常值，有哪些方法可以进行有效处理？

    使用ARIMA模型进行预测时，如何解读模型的残差图？
    在ARIMA模型中，如何选择合适的差分阶数d？
    如何使用Python的statsmodels库进行时间序列的ADF检验？
    如果残差图中出现了周期性波动，我应该如何调整ARIMA模型？
    在ARIMA模型中，如何判断是否需要添加季节性项（SARIMA）？

    如何使用Python中的statsmodels库进行季节性分解？
    在季节性周期不规律时，有哪些方法可以调整或识别这种模式？
    季节性周期的确定对于时间序列预测的准确性有多大影响？

数据处理：
    使用MinMaxScaler时如何处理异常值？
    归一化对于机器学习算法性能的影响是什么？
    如何判断一个数据集是否需要进行异常值处理？