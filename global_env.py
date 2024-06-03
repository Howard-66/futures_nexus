import platform

CurrentSystem = platform.system()
# 顶部导航栏高度
HeaderHeight = 50
# 左侧导航栏宽度
NavbarWidth = 240
# 右侧侧边栏宽度
AsideWidth = 300
# 主内容区域高度
MainContentHeight = 1250 if CurrentSystem=='Darwin' else 680
# 主内容内部顶边距
MainContentPaddingTop = 50
# 主内容背景颜色
MainContentBGColor = "#f5f5f5"
# 交易笔记编辑区域高度
NoteEditHeight = 450 if CurrentSystem=='Darwin' else 300

# 期限结构图表高度
TermStrctureFigureHeight = 120 if CurrentSystem=='Darwin' else 80
# 跨期分析图表高度
CrossTermFigureHeight = 400 if CurrentSystem=='Darwin' else 280

PrimaryLongColor = "#FF434D"
SecondaryLongColor = "#FDC5CB"
PrimaryShortColor = "#1E887C"
SecondaryShortColor = "#C2E5E1"
PrimaryLineColor = "#0873e5"
SecondaryLineColor = "#E8752F"
PrimaryNeutralColor = "#d3d3d3"