# -*- coding: utf-8 -*-
# @Time : 2021/1/18 0018 10:35
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : main.py
# @Project : Taobao
from ClsTaobao import *
import os
import time
import shutil



def testFunc():
    pass


if __name__ == '__main__':

    # 调用测试方法
    testFunc()
    exit(0)

    # 定义工作目录和程序主目录
    mainDir = os.getcwd()
    os.chdir('work')
    workDir = os.getcwd()
    os.chdir(mainDir)


    # 备份工作目录
    print('【备份工作目录】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
    tmid = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    workBakDir = 'work-' + tmid
    os.mkdir(workBakDir)
    os.chdir(workBakDir)
    workBakAbsDir = os.getcwd()
    os.chdir(mainDir)
    os.removedirs(workBakAbsDir)
    print(workDir,workBakAbsDir)
    shutil.copytree(workDir,workBakAbsDir)
    print('【备份工作目录】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))


    # 初始化taobao对象
    taobao = Taobao()
    # 定义xls文件存放目录
    xlsDir = workDir + '\\'
    xlsList = []

    # 1. xls转xlsx
    # 获取工作目录下所有xls文件名称
    xlsList = taobao.get_path_xls(xlsDir)
    print('【xls转xlsx】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
    for xls in xlsList:
        # 拼接xls绝对路径
        xlsAbsPath = xlsDir + xls
        taobao.xls_to_xlsx(xlsAbsPath)
    print('【xls转xlsx】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

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
        if int(ws.nrows)-1 == cnt:
            os.remove(xlsxAbsPath)
            print('所有订单号均存在于数据库中，已删除文件',xlsxAbsPath)
    print('【删除文件】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

    # 4. 导入数据
    # 获取工作目录下所有xlsx文件名称
    xlsxList = taobao.get_path_xlsx(xlsDir)
    print('【文件导入】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
    for xlsx in xlsxList:
        xlsxAbsPath = xlsDir + xlsx
        print(xlsxAbsPath,'处理中……')
        # 删除订单号为空的行
        taobao.delBlankOrderRow(xlsxAbsPath)
        cnt = int(taobao.importData(xlsxAbsPath))
        if cnt > 0:
            os.remove(xlsxAbsPath)
            print('订单导入完毕，删除',xlsxAbsPath)
    print('【文件导入】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))