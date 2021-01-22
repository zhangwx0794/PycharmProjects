# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:33
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : repeTaskCheck.py
# @Project : TaobaoSDMS
from flask import Blueprint, render_template, request
from models.mysql_func import *
from models.zhangwx import *
import os, datetime, xlrd
from dateutil.relativedelta import relativedelta

repeTaskCheck = Blueprint('repeTaskCheck', __name__, template_folder='../templates/')


@repeTaskCheck.route('', methods=['GET', 'POST'])
def _repeTaskCheck():
    if request.method == 'POST':
        file = request.files.get("file")
        if file.filename is '':
            # 表示没有发送文件
            checkRes = [-1, '错误，未上传文件']
        elif str(file.filename).split('.')[-1] not in ('xls', 'xlsx'):
            checkRes = [-1, '错误，文件类型不是xls或者xlsx']
        else:
            os.getcwd()
            basepath = os.getcwd()  # 当前文件所在路径
            if getSystemPlatform() == 'Windows':
                uploadDir = basepath + '\\static\\uploads'
            else:
                uploadDir = basepath + '/static/uploads'
            if not os.path.exists(uploadDir):
                os.mkdir(uploadDir)
            if getSystemPlatform() == 'Windows':
                uploadPath = uploadDir + '\\' + file.filename
            else:
                uploadPath = uploadDir + '/' + file.filename
            # uploadPath = os.path.join(basepath, 'static\\uploads', secure_filename(file.filename))
            file.save(uploadPath)
            wb = xlrd.open_workbook(uploadPath)
            # * 打开第一个sheet
            ws = wb.sheet_by_index(0)
            repeTaskList = []
            for line in range(1, ws.nrows):
                wangWangId = str(ws.cell_value(rowx=line, colx=0)).strip()
                shopName = str(ws.cell_value(rowx=line, colx=1)).strip()
                dateTurple = xlrd.xldate_as_tuple(ws.cell_value(rowx=line, colx=2), 0)
                year, month, day = dateTurple[:3]
                lastMonthDate = str(datetime.date(year, month, day) - relativedelta(months=+1))
                taskDate = str(dateTurple[0]) + '-' + str(dateTurple[1]).rjust(2, '0') + '-' + str(dateTurple[2]).rjust(
                    2, '0')
                sqlFormat = 'wangwangId=' + '\'' + wangWangId + '\'' + 'and shopName=' + '\'' + shopName + '\'' + 'and date >' + '\'' + lastMonthDate + '\''
                sql = 'select wangwangId,shopName,orderId,date from orderInfo where isDel = 0 and {0}'.format(sqlFormat)
                sqlRes = mysql_conn(sql)
                # 删除用户上传的任务检查表
                os.remove(uploadPath)
                if len(sqlRes) > 0:
                    tp = (wangWangId, shopName, taskDate, sqlRes[0][2], sqlRes[0][3])
                    repeTaskList.append(tp)
                    checkRes = [1, repeTaskList]
                else:
                    checkRes = [-1, '恭喜你，本excel中所有旺旺ID 1个月内无重复任务！']
    elif request.method == 'GET':
        checkRes = [-1, '']
    return render_template('repeTaskCheck.html', checkRes=checkRes)
