# Futures Nexus
Futures Nexus is a futures quantitative analysis and investment platform based on the "basis-inventory-profit" model. It offers fundamental analysis, cyclical analysis, inter-commodity analysis, inter-period analysis, industry chain analysis, and comes with built-in fundamental analysis indicators. The platform supports the download of fundamental data for futures and integrates both fundamental and technical analysis to specify trading plans.

Futures Nexus是一款基于“基差-库存-利润”模式的期货量化分析和投资平台，可以提供基本面分析、周期性分析、跨期分析、跨品种分析、产业链分析，内置基本面分析指标，支持期货基本面数据下载，并通过基本面和技术面融合分析，指定交易计划。

TODO:
- 补齐仓单/库存的空数据
- 合并AKshare和Choice的库存、仓单数自动初始化产业链，
- 实现品种的快速访问：快速入口，搜索栏，自动初始化所属产业链页面数据

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