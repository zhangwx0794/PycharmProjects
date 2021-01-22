# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:29
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : 404.py
# @Project : TaobaoSDMS
from flask import Blueprint, render_template

# 注册蓝图
NF404 = Blueprint('NF404', __name__, template_folder='../templates/')

@NF404.route('',methods=['GET', 'POST'])
def _NF404():
    return render_template('404.htm')