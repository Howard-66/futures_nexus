import platform

CurrentSystem = platform.system()
HeaderHeight = 70
NavbarWidth = 240
AsideWidth = 300
MainContentHeight = 1250 if CurrentSystem=='Darwin' else 680
MainContentPaddingTop = 70
MainContentBGColor = "#f5f5f5"