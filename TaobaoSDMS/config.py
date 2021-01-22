# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 13:22
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : config.py
# @Project : TaobaoSDMS

import os
from datetime import timedelta


class Config(object):
    # 设置秘钥
    SECRET_KEY = os.urandom(24)
    # 设置session 1小时过期
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    # Debug
    DEBUG = True
