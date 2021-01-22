# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 14:44
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : downloadExcel.py
# @Project : TaobaoSDMS
from flask import Blueprint, request,send_file
from models.mysql_func import *
from models.zhangwx import *
import io,uuid,time
import xlsxwriter

downloadExcel = Blueprint('downloadExcel', __name__, template_folder='../templates/')


@downloadExcel.route('', methods=['GET', 'POST'])
def _downloadExcel():
    # 获取url参数信息
    print('/downloadExcel', request.args)
    userUuid = request.args.get('uuid')
    goodsName = request.args.get('goodsName')
    goodsKey = request.args.get('goodsKey')
    wangwangId = request.args.get('wangwangId')
    orderId = request.args.get('orderId')
    shopName = request.args.get('shopName')
    date = request.args.get('date')
    handlerName = request.args.get('handlerName')
    custName = request.args.get('custName')
    opWechatId = request.args.get('opWechatId')
    note = request.args.get('note')
    searchSql = ''
    if goodsName != '':
        searchSql = searchSql + ' and goodsName like ' + '\'' + goodsName + '%\''
    if goodsKey != '':
        searchSql = searchSql + ' and goodsKey like ' + '\'' + goodsKey + '%\''
    if wangwangId != '':
        searchSql = searchSql + ' and wangwangId like ' + '\'' + wangwangId + '%\''
    if orderId != '':
        searchSql = searchSql + ' and orderId like ' + '\'' + orderId + '%\''
    if shopName != '':
        searchSql = searchSql + ' and shopName like ' + '\'' + shopName + '%\''
    if date != '':
        searchSql = searchSql + ' and date like ' + '\'' + date + '%\''
    if handlerName != '':
        searchSql = searchSql + ' and handlerName like ' + '\'' + handlerName + '%\''
    if custName != '':
        searchSql = searchSql + ' and custName like ' + '\'' + custName + '%\''
    if opWechatId != '':
        searchSql = searchSql + ' and opWechatId like ' + '\'' + opWechatId + '%\''
    if note != '':
        searchSql = searchSql + ' and note like ' + '\'' + note + '%\''

    # 根据UUID查询角色信息，如果是管理员则导出内部可见列，普通角色不导出内部可见列
    username = getSessionValue('username')
    role = getUserRole(username)

    if role == 9:
        header_list = ["序号", "店铺名称", "宝贝标题", "关键词", "旺旺", "订单号", "实付金额", "佣金", "红包及其他", "刷手佣金", "经手人", "操作微信号", "客户名称",
                       "日期","备注" ]
        # 拼接form参数sql
        whereSql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date,note from orderInfo where isDel = 0 {0}'.format(
        searchSql)
    else:
        header_list = ["序号", "店铺名称", "宝贝标题", "关键词", "旺旺", "订单号", "实付金额", "佣金", "客户名称", "日期","备注" ]
        # 拼接form参数sql
        whereSql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,custName,date,note from orderInfo where isDel = 0 {0}'.format(
            searchSql)
    # 获取查询结果
    searchData = mysql_conn(whereSql)
    """1. 生成表头   2. 生成数据  3. 个性化合并单元格，修改字体属性、修改列宽  3. 返回给前端"""
    fp = io.BytesIO()  # 生成一个BytesIO对象
    book = xlsxwriter.Workbook(fp)  # 可以认为创建了一个Excel文件
    worksheet = book.add_worksheet('sheet1')  # 增加一个sheet
    # 1. 生成表头
    for col, header in enumerate(header_list):
        worksheet.write(0, col, header)  # 行(从0开始), 列(从0开始)， 内容

    # 2. 生成数据
    x = 1
    # print('searchData type is',type(searchData))
    # print('searchData value is',searchData)
    for orderInfo in searchData:
        y = 0
        # print('orderInfo values is ',orderInfo)
        for cellInfo in orderInfo:
            # print('cellInfo value is ',cellInfo)
            worksheet.write(x, y, cellInfo)  # 遍历导入每条订单信息
            y += 1
        x += 1

    # 3. 个性化合并单元格，修改字体属性、修改列宽
    # 定义格式实例, 16号字体，加粗，水平居中，垂直居中，红色字体
    my_format = book.add_format(
        {'font_size': 16, 'bold': True, 'align': 'center', 'valign': 'vcenter', "font_color": "red"})
    # worksheet.merge(len(students_data + 1, students_data + 2, 1, 5, "合并单元格内容", my_format))
    book.close()
    fp.seek(0)
    fileName = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time())) + '_' + ''.join(
        str(uuid.uuid4()).split('-')) + '.xlsx'
    return send_file(fp, attachment_filename=fileName, as_attachment=True)
