# -*- coding: utf-8 -*-
# 获取当前系统类型
import platform
import hashlib
def getSystemPlatform():
    plat_tuple = platform.architecture()
    system = platform.system()
    return system



# 简单版的md5加密返回密文函数
def getMd5(pw):
    md = hashlib.md5()  # 生成md5对像
    md.update(pw.encode('utf-8'))  # 加密，加密密码的时候，必须对密码进行编码，否则会报错
    return md.hexdigest()  # 返回16进制密文