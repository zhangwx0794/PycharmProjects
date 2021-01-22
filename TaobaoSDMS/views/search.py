# -*- coding: utf-8 -*-
# @Time : 2021/1/22 0022 15:49
# @Author : Owen
# @Email : zhangwx0794@gmail.com
# @File : search.py
# @Project : TaobaoSDMS
from flask import Flask, render_template, request, redirect, url_for,Blueprint
from models.mysql_func import *
from models.zhangwx import *

search = Blueprint('search',__name__,template_folder='../templates/')

@search.route('',methods=['GET','POST'])
def _search():
    if sessionCheck():
        username = getSessionValue('username')
        userUuid = getUserUuid(username)
    else:
        return redirect('/login')

    # 页面重定向，如果UUID是管理员则显示更多属性，如果没有UUID则跳转404，否则显示普通属性
    # 获取UUID
    formParameters = []
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
            note = form['note']
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
            formParameters.append(note)
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
            # 本次查询结果总记录数
            queryTotalCntSql = 'select count(0) from orderInfo where isDel = 0 {0}'.format(searchSql)
            queryTotalCnt = int(mysql_conn(queryTotalCntSql)[0][0])
        elif request.method == 'GET':
            searchSql = ''
            queryTotalCnt = 0

        # 计算最大页数
        maxPage = count_max_page(tableName='orderInfo', pageSize=pageSize)
        paginateDict = paginate(page=page, size=pageSize)
        sql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date,note from orderInfo where isDel = 0 {0} order by date desc,shopName,id limit {1},{2}'.format(
            searchSql, paginateDict['offset'], paginateDict['limit'])
        print(sql)
        sqlRes = mysql_conn(sql)
        lastPage = paginateDict['before']
        nextPage = paginateDict['next']

        # 计算查询结果订单总价格
        priceSql = 'select id,shopName,goodsName,goodsKey,wangwangId,orderId,goodsPrice,goodsYj,redPackets,ssyj,handlerName,opWechatId,custName,date,note from orderInfo where isDel = 0 {0}'.format(
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
            formParameters=formParameters,
            username=username
        )