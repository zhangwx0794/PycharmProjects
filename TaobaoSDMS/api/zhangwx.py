# -*- coding: utf-8 -*-
# 获取当前系统类型
import platform
def getSystemPlatform():
    plat_tuple = platform.architecture()
    system = platform.system()
    return system