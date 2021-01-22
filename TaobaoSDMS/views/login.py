# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:05
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : login.py
# @Project : TaobaoSDMS

from flask import Blueprint, render_template, request
from models.mysql_func import *
from models.zhangwx import *

# 注册蓝图
login = Blueprint('login', __name__, template_folder='../templates/')

@login.route('',methods=['GET', 'POST'])
def _login():
    username = ''
    password = ''
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = getMd5(request.form.get('password'))
        if userLoginCheck(username, password) == 1:
            # 将用户名存入session
            session['username'] = username
            if getSessionValue('url') != '':
                return getSessionValue('url')
            else:
                return defaultPage
        else:
            return 'fail'
