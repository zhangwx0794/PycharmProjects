# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:44
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : downloadExcel.py
# @Project : TaobaoSDMS
from flask import Blueprint, request, send_from_directory,send_file
from models.zhangwx import *

downloadImportTemplate = Blueprint('downloadImportTemplate', __name__, template_folder='../templates/')


@downloadImportTemplate.route('', methods=['GET', 'POST'])
def _downloadImportTemplate():
    # 获取url参数信息

    print('/downloadImportTemplate', request.args)
    if getSystemPlatform() == 'Linux':
        return send_file('static/download/2000-01-01导入模板.xlsx',as_attachment=True)
    else:
        return send_from_directory(directory=r'static\download',filename='2000-01-01导入模板.xlsx',as_attachment=True)
    # return send_from_directory("../static/download/",filename="2000-01-01导入模板.xlsx",as_attachment=True)

