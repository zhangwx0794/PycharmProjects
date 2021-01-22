# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 15:56
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : importData.py
# @Project : TaobaoSDMS

from flask import Flask, render_template, request, redirect, Blueprint
from models.zhangwx import *
from models.ClsTaobao import *
import os, time, shutil

importData = Blueprint('importData', __name__, template_folder='../templates/')


@importData.route('', methods=['GET', 'POST'])
def _importData():
    if sessionCheck():
        pass
    else:
        session['url'] = '/importData'
        return redirect('/login')

    importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
    checkRes = ['1', '']
    dataImportNum = 0
    if request.method == 'POST':
        file = request.files.get("file")
        if file.filename is '':
            # 表示没有发送文件
            checkRes = [-1, '错误，未上传文件']
            return render_template('importData.html', importData=importData, dataImportNum=dataImportNum,
                                   checkRes=checkRes)
        elif str(file.filename).split('.')[-1] not in ('xls', 'xlsx'):
            checkRes = [-1, '错误，文件类型不是xls或者xlsx']
            return render_template('importData.html', importData=importData, dataImportNum=dataImportNum,
                                   checkRes=checkRes)
        else:
            os.getcwd()
            basepath = os.getcwd()  # 当前文件所在路径
            if getSystemPlatform() == 'Windows':
                uploadDir = basepath + '\\work'
            else:
                uploadDir = basepath + '/work'
            if not os.path.exists(uploadDir):
                os.mkdir(uploadDir)
            if getSystemPlatform() == 'Windows':
                uploadPath = uploadDir + '\\' + file.filename
            else:
                uploadPath = uploadDir + '/' + file.filename
            # uploadPath = os.path.join(basepath, 'static\\uploads', secure_filename(file.filename))
            file.save(uploadPath)

            # 初始化taobao对象
            taobao = Taobao()
            # 创建工作目录

            if taobao.getSystemPlatform() == 'Windows':
                if not os.path.exists(os.getcwd() + '\\work'):
                    os.mkdir(os.getcwd() + '\\work')
            else:
                if not os.path.exists('/boss/soft/taobao/work'):
                    os.mkdir('/boss/soft/taobao/work')

            # 定义工作目录和程序主目录
            if taobao.getSystemPlatform() == 'Windows':
                mainDir = os.getcwd()
                os.chdir('work')
                workDir = os.getcwd()
                os.chdir(mainDir)
            else:
                mainDir = '/boss/soft/taobao'
                workDir = '/boss/soft/taobao/work'

            # 定义xls文件存放目录
            xlsList = []
            if taobao.getSystemPlatform() == 'Windows':
                xlsDir = workDir + '\\'
            else:
                xlsDir = workDir + '/'
            # # 1. xls转xlsx
            # # 获取工作目录下所有xls文件名称
            # xlsList = taobao.get_path_xls(xlsDir)
            # print('【xls转xlsx】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
            # for xls in xlsList:
            #     # 拼接xls绝对路径
            #     xlsAbsPath = xlsDir + xls
            #     taobao.xls_to_xlsx(xlsAbsPath)
            # print('【xls转xlsx】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

            # 2. 检查文件命名规范，重命名文件
            # 获取工作目录下所有xlsx文件名称
            xlsxList = taobao.get_path_xlsx(xlsDir)
            print('【检查文件命名规范&重命名】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
            for xlsx in xlsxList:
                xlsxAbsPath = xlsDir + xlsx
                taobao.format_xls_name(xlsxAbsPath)
            print('【检查文件命名规范&重命名】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

            # 3. 删除文件中所有订单号都在数据库中已存在的文件
            xlsxList = taobao.get_path_xlsx(xlsDir)
            print('【删除文件】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
            for xlsx in xlsxList:
                xlsxAbsPath = xlsDir + xlsx
                # 删除订单号为空的行
                taobao.delBlankOrderRow(xlsxAbsPath)
                # * 打开excel
                wb = xlrd.open_workbook(xlsxAbsPath)
                # * 打开第一个sheet
                ws = wb.sheet_by_index(0)
                cnt = taobao.chkXlsOrderUniq(xlsxAbsPath)
                if int(ws.nrows) - 1 == cnt:
                    os.remove(xlsxAbsPath)
                    print('所有订单号均存在于数据库中，已删除文件', xlsxAbsPath)
                    checkRes = [-1, '导入失败，所有订单号均存在于数据库中']
                    return render_template('importData.html', importData=importData, dataImportNum=dataImportNum,
                                           checkRes=checkRes)

            print('【删除文件】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

            # 4. 导入数据
            # 获取工作目录下所有xlsx文件名称
            xlsxList = taobao.get_path_xlsx(xlsDir)
            print('【文件导入】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))

            for xlsx in xlsxList:
                xlsxAbsPath = xlsDir + xlsx
                print(xlsxAbsPath, '处理中……')
                # 删除订单号为空的行
                print('开始删除订单号为空的行')
                taobao.delBlankOrderRow(xlsxAbsPath)
                print('结束删除订单号为空的行')
                dataImportNum = int(taobao.importData(xlsxAbsPath))
                print(xlsx, '成功导入{0}条数据'.format(dataImportNum))
                if dataImportNum > 0:
                    os.remove(xlsxAbsPath)
                    print('订单导入完毕，删除', xlsxAbsPath)
            print('【文件导入】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))
            importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
            # 如果是从POST来的请求，并且导入0条数据，dataImportNum=-1 表示导入失败
            if dataImportNum == 0:
                dataImportNum = -1
    elif request.method == 'GET':
        importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
        cnt = 0
    return render_template('importData.html', importData=importData, dataImportNum=dataImportNum, checkRes=checkRes)
