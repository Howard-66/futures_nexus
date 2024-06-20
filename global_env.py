import platform

CurrentSystem = platform.system()
# 顶部导航栏高度
HeaderHeight = 50
# 左侧导航栏宽度
NavbarWidth = 240
# 右侧侧边栏宽度
AsideWidth = 300
# 主内容区域高度
MainContentHeight = 1250 if CurrentSystem=='Darwin' else 980
# 主内容内部顶边距
MainContentPaddingTop = 50
# 交易笔记编辑区域高度
NoteEditHeight = 450 if CurrentSystem=='Darwin' else 400

# 期限结构图表高度
TermStrctureFigureHeight = 120
# 跨期分析图表高度
CrossTermFigureHeight = 400 if CurrentSystem=='Darwin' else 350


# 最大加载K线数量
MaxLoadingBars = 500
# 显示最近K线数量
DisplayLastBars = 400
# 指标回溯计算窗口
TraceBackWindow = 240
# 季节周期
SeasonalWindow = 240
# 超买线阈值
OverBuy = 0.8
# 超卖线阈值
OverSell = 0.2

# 主内容背景颜色
MainContentBGColor = "#f5f5f5"
# 多头主配色
PrimaryLongColor = "#FF434D"
# 多头次配色
SecondaryLongColor = "#FDC5CB"
# 空头主配色
PrimaryShortColor = "#22ac9c"
# 空头次配色
SecondaryShortColor = "#C2E5E1"
# 中性主配色
PrimaryNeutralColor = "#d3d3d3"
# 线主配色
PrimaryLineColor = "#0873e5"
# 线次配色
SecondaryLineColor = "#FF770E"