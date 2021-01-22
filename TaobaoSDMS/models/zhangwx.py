# -*- coding: utf-8 -*-
# 获取当前系统类型
from flask import Flask, session
import platform
import hashlib



# 获取系统平台
def getSystemPlatform():
    plat_tuple = platform.architecture()
    system = platform.system()
    return system


# 简单版的md5加密返回密文函数
def getMd5(pw):
    md = hashlib.md5()  # 生成md5对像
    md.update(pw.encode('utf-8'))  # 加密，加密密码的时候，必须对密码进行编码，否则会报错
    return md.hexdigest()  # 返回16进制密文


# 定义登录跳转默认页
defaultPage = '/search'


# 检查session中是否还有用户
def sessionCheck():
    return True if 'username' in dict(session).keys() else False


# 根据key获取session值
def getSessionValue(key):
    if key in dict(session).keys():
        return session[key]
    else:
        return ''


# 清空session
def deleteAllSession():
    keys = dict(session).keys()
    for key in keys:
        dict(session).pop(key)
    print('deleteAllSession')
