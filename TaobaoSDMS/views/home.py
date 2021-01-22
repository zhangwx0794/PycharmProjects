# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:05
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : login.py
# @Project : TaobaoSDMS

from flask import Blueprint, render_template

# 注册蓝图
home = Blueprint('home', __name__, template_folder='../templates/')

@home.route('',methods=['GET', 'POST'])
def _home():
    return render_template('login.html')
