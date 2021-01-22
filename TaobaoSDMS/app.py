# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from models.mysql_func import *
from models.zhangwx import *
from models.ClsTaobao import *
from views.login import login
from views.logout import logout
from views.home import home
from views.NF404 import NF404
from models.downloadExcel import downloadExcel
from models.downloadImportTemplate import downloadImportTemplate
from views.repeTaskCheck import repeTaskCheck
from views.search import search
from views.importData import importData

from config import Config

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 注册蓝图
app.register_blueprint(login, url_prefix='/login')
app.register_blueprint(logout, url_prefix='/logout')
app.register_blueprint(home, url_prefix='/home')
app.register_blueprint(NF404, url_prefix='/404')
app.register_blueprint(NF404, url_prefix='/404')
app.register_blueprint(repeTaskCheck, url_prefix='/repeTaskCheck')
app.register_blueprint(downloadExcel, url_prefix='/downloadExcel')
app.register_blueprint(search, url_prefix='/search')
app.register_blueprint(importData, url_prefix='/importData')
app.register_blueprint(downloadImportTemplate, url_prefix='/downloadImportTemplate')


if __name__ == '__main__':
    app.run(debug=True)
