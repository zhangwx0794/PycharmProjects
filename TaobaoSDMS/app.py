# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from api.mysql_func import *
from api.zhangwx import *
import api.importData
import xlsxwriter
import uuid
import io
import os
import time, datetime
from dateutil.relativedelta import relativedelta
import xlwt, xlrd
from api.ClsTaobao import *
import os
import time
import shutil

app = Flask(__name__)


@app.route('/')
def home():
    # 页面重定向
    userUuid = request.args.get('uuid')
    if check_user(userUuid):
        return redirect(url_for('search', uuid=userUuid))
    else:
        return redirect(url_for('error404'))


@app.route('/404')
def error404():
    return render_template('404.htm')


@app.route('/index')
def index():
    # 每页显示数量 page_show_count
    page_show_count = int(request.args.get('page_show_count')) if request.args.get('page_show_count') != None else 15
    page = int(request.args.get('page')) if request.args.get('page') != None else 1
    # 计算最大页数
    sql_row_count = 'select count(0) from orderInfo where isDel = 0'
    maxPage = (mysql_conn(sql_row_count)[0][0] % page_show_count) / page_show_count if mysql_conn(sql_row_count)[0][
                                                                                           0] % page_show_count == 0 else int(
        mysql_conn(sql_row_count)[0][0] / page_show_count) + 1
    sql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,handlerName,date from orderInfo where isDel = 0 order by date limit %s,%s' % (
        str((page - 1) * page_show_count), page_show_count)
    print('打印sql语句: ', sql)
    sqlRes = mysql_conn(sql)
    lastPage = page - 1 if page > 1 else 1
    nextPage = page + 1 if page < maxPage else maxPage
    print(page, lastPage, nextPage, maxPage)
    return render_template('index.html', sqlRes=sqlRes, lastPage=lastPage, nextPage=nextPage, maxPage=maxPage)


@app.route('/search', methods=["GET", "POST"])
def search():
    # 页面重定向，如果UUID是管理员则显示更多属性，如果没有UUID则跳转404，否则显示普通属性
    # 获取UUID
    userUuid = ''
    role = 0
    formParameters = []
    if request.method == 'GET':
        userUuid = request.args.get('uuid')
    elif request.method == 'POST':
        userUuid = request.form['userUuid']

    if not check_user(userUuid):
        return redirect(url_for('error404'))
    else:
        # 根据UUID获取角色值 9为管理员|0普通用户
        role = int(mysql_conn('select role from userInfo where uuid = {0}'.format('\'' + userUuid + '\''))[0][0])
        # 初始化变量page和pageSize
        if request.method == 'POST':
            form = request.form
            pageSize = int(form['pageSize'])
            page = 1
        elif request.method == 'GET':
            # 如果url中传过来的pageSize为空则每页显示10条数据
            pageSize = int(request.args.get('pageSize')) if request.args.get('pageSize') != None else 10
            # 如果url中传过来的page为空则显示第1页
            page = int(request.args.get('page')) if request.args.get('page') != None else 1
        else:
            page = 1
            pageSize = 10
        # 获取前端传入的模糊查询变量并计算查询结果数量
        if request.method == 'POST':
            form = request.form
            goodsName = form['goodsName']
            goodsKey = form['goodsKey']
            wangwangId = form['wangwangId']
            orderId = form['orderId']
            shopName = form['shopName']
            date = form['date']
            handlerName = form['handlerName']
            custName = form['custName']
            opWechatId = form['opWechatId']
            # 将前端查询参数写到数组里
            formParameters.append(goodsName)
            formParameters.append(goodsKey)
            formParameters.append(wangwangId)
            formParameters.append(orderId)
            formParameters.append(shopName)
            formParameters.append(date)
            formParameters.append(handlerName)
            formParameters.append(custName)
            formParameters.append(opWechatId)
            searchSql = ''
            if goodsName != '':
                searchSql = searchSql + ' and goodsName like ' + '\'%' + goodsName + '%\''
            if goodsKey != '':
                searchSql = searchSql + ' and goodsKey like ' + '\'%' + goodsKey + '%\''
            if wangwangId != '':
                searchSql = searchSql + ' and wangwangId like ' + '\'%' + wangwangId + '%\''
            if orderId != '':
                searchSql = searchSql + ' and orderId like ' + '\'%' + orderId + '%\''
            if shopName != '':
                searchSql = searchSql + ' and shopName like ' + '\'%' + shopName + '%\''
            if date != '':
                searchSql = searchSql + ' and date like ' + '\'%' + date + '%\''
            if handlerName != '':
                searchSql = searchSql + ' and handlerName like ' + '\'%' + handlerName + '%\''
            if custName != '':
                searchSql = searchSql + ' and custName like ' + '\'%' + custName + '%\''
            if opWechatId != '':
                searchSql = searchSql + ' and opWechatId like ' + '\'%' + opWechatId + '%\''
            # 本次查询结果总记录数
            queryTotalCntSql = 'select count(0) from orderInfo where isDel = 0 {0}'.format(searchSql)
            queryTotalCnt = int(mysql_conn(queryTotalCntSql)[0][0])
        elif request.method == 'GET':
            searchSql = ''
            queryTotalCnt = 0

        # 计算最大页数
        maxPage = count_max_page(tableName='orderInfo', pageSize=pageSize)
        paginateDict = paginate(page=page, size=pageSize)
        sql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date from orderInfo where isDel = 0 {0} order by date limit {1},{2}'.format(
            searchSql, paginateDict['offset'], paginateDict['limit'])
        sqlRes = mysql_conn(sql)
        lastPage = paginateDict['before']
        nextPage = paginateDict['next']

        # 计算分页订单总价格
        priceSql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date from orderInfo where isDel = 0 {0} order by date'.format(
            searchSql)
        priceSqlRes = mysql_conn(priceSql)
        totalKdjPrice = 0
        totalYjPrice = 0
        totalRedPackets = 0
        totalSsyj = 0
        for tp in priceSqlRes:
            totalKdjPrice += tp[6]
            totalYjPrice += tp[7]
            totalRedPackets += tp[8]
            totalSsyj += tp[9]

        return render_template(
            'search.html',
            queryTotalCnt=queryTotalCnt,
            sqlRes=sqlRes,
            lastPage=lastPage,
            nextPage=nextPage,
            maxPage=maxPage,
            pageSize=pageSize,
            totalKdjPrice=totalKdjPrice,
            totalYjPrice=totalYjPrice,
            totalRedPackets=totalRedPackets,
            totalSsyj=totalSsyj,
            role=role,
            formParameters=formParameters
        )


@app.route("/search/downloadExcel", methods=["GET"])
def download_excel():
    # 获取url参数信息
    print('/search/downloadExcel', request.args)
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
    searchSql = ''
    if goodsName != '':
        searchSql = searchSql + ' and goodsName like ' + '\'%' + goodsName + '%\''
    if goodsKey != '':
        searchSql = searchSql + ' and goodsKey like ' + '\'%' + goodsKey + '%\''
    if wangwangId != '':
        searchSql = searchSql + ' and wangwangId like ' + '\'%' + wangwangId + '%\''
    if orderId != '':
        searchSql = searchSql + ' and orderId like ' + '\'%' + orderId + '%\''
    if shopName != '':
        searchSql = searchSql + ' and shopName like ' + '\'%' + shopName + '%\''
    if date != '':
        searchSql = searchSql + ' and date like ' + '\'%' + date + '%\''
    if handlerName != '':
        searchSql = searchSql + ' and handlerName like ' + '\'%' + handlerName + '%\''
    if custName != '':
        searchSql = searchSql + ' and custName like ' + '\'%' + custName + '%\''
    if opWechatId != '':
        searchSql = searchSql + ' and opWechatId like ' + '\'%' + opWechatId + '%\''

    # 拼接form参数sql
    whereSql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date from orderInfo where isDel = 0 {0}'.format(
        searchSql)
    # 获取查询结果
    searchData = mysql_conn(whereSql)

    # 根据UUID查询角色信息，如果是管理员则导出内部可见列，普通角色不导出内部可见列
    header_list = []
    role = int(mysql_conn('select role from userInfo where uuid = {0}'.format('\'' + userUuid + '\''))[0][0])
    if role == 9:
        header_list = ["序号", "店铺名称", "宝贝标题", "关键词", "旺旺", "订单号", "实付金额", "佣金", "红包及其他", "刷手佣金", "经手人", "操作微信号", "客户名称",
                       "日期"]
    else:
        header_list = ["序号", "店铺名称", "宝贝标题", "关键词", "旺旺", "订单号", "实付金额", "佣金", "客户名称", "日期", ]
    """1. 生成表头   2. 生成数据  3. 个性化合并单元格，修改字体属性、修改列宽  3. 返回给前端"""
    fp = io.BytesIO()  # 生成一个BytesIO对象
    book = xlsxwriter.Workbook(fp)  # 可以认为创建了一个Excel文件
    worksheet = book.add_worksheet('sheet1')  # 增加一个sheet
    # 1. 生成表头
    header_list = ["序号", "店铺名称", "宝贝标题", "关键词", "旺旺", "订单号", "实付金额", "佣金", "红包及其他", "刷手佣金", "经手人", "操作微信号", "客户名称",
                   "日期"]
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


@app.route("/repeTaskCheck", methods=["GET", 'POST'])
def repeTaskCheck():
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


@app.route("/importData", methods=["GET", 'POST'])
def importData():
    importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
    cnt = 0
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

            # 备份工作目录
            print('【备份工作目录】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))
            tmid = str(time.strftime('%Y_%m_%d_%H_%M_%S'))
            workBakDir = 'work-' + tmid
            if taobao.getSystemPlatform() == 'Windows':
                os.mkdir(workBakDir)
                os.chdir(workBakDir)
                workBakAbsDir = os.getcwd()
                os.chdir(mainDir)
                print(workDir, workBakAbsDir)
            else:
                workBakAbsDir = '/boss/soft/taobao/' + workBakDir
                print(workDir, workBakAbsDir)
            shutil.copytree(workDir, workBakAbsDir)
            print('【备份工作目录】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

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
            print('【删除文件】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))

            # 4. 导入数据
            # 获取工作目录下所有xlsx文件名称
            xlsxList = taobao.get_path_xlsx(xlsDir)
            print('【文件导入】工作开始', time.strftime('%Y-%m-%d %H:%M:%S'))

            for xlsx in xlsxList:
                xlsxAbsPath = xlsDir + xlsx
                print(xlsxAbsPath, '处理中……')
                # 删除订单号为空的行
                taobao.delBlankOrderRow(xlsxAbsPath)
                cnt = int(taobao.importData(xlsxAbsPath))
                if cnt > 0:
                    os.remove(xlsxAbsPath)
                    print('订单导入完毕，删除', xlsxAbsPath)
            print('【文件导入】工作结束', time.strftime('%Y-%m-%d %H:%M:%S'))
            importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
            # 如果是从POST来的请求，并且导入0条数据，那么赋值cnt=-1 表示导入失败
            if cnt == 0:
                cnt = -1
    elif request.method == 'GET':
        importData = [('', '', '', '', '', '', '', '', '', '', '', '', '', '')]
        cnt = 0
    return render_template('importData.html', importData=importData,cnt=cnt)


if __name__ == '__main__':
    app.run(debug=True)
