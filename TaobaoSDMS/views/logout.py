# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:16
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : logout.py
# @Project : TaobaoSDMS
from flask import Blueprint, render_template, request
from models.zhangwx import *

# 注册蓝图
logout = Blueprint('logout', __name__, template_folder='../templates/')


@logout.route('', methods=['GET', 'POST'])
def _logout():
    if request.method == 'POST':
        if sessionCheck():
            deleteAllSession()
            return 'success'
    else:
        return render_template('login.html')
