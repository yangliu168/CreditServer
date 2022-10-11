# encoding: utf-8

import time
import datetime
import random
from django.shortcuts import render
import json
from django.views import View
from django.http import JsonResponse
import redis
from threading import Thread
from multiprocessing import Process
import pymysql
import re
from .get_elements_data import get_user_scores
import configparser
import os

# 获取配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('myconfig.ini', 'w', encoding="utf-8") as f:
    with open(BASE_DIR + '/config.ini', 'r', encoding="utf-8") as con_f:
        f.write(con_f.read())
conf = configparser.ConfigParser()
conf.read('myconfig.ini', encoding="utf-8")
envi_config = conf['envi']
envi = envi_config.get('envi', 'local')
mysql_config = conf[envi + '_mysql']
redis_config = conf[envi + '_redis']
mission_config = conf['mission']
update_credit_score_quantity = mission_config.get('update_credit_score_quantity', 1000)

# 调度任务状态标记
mission_statu = 1


def connect_mysql():
    """
    连接数据库
    """
    for i in range(5):
        try:
            db = pymysql.connect(
                host=mysql_config.get('HOST', None),
                port=int(mysql_config.get('PORT', None)),
                user=mysql_config.get('USER', None),
                password=mysql_config.get('PASSWORD', None),
                database=mysql_config.get('NAME', None),
                charset="utf8")
        except Exception as e:
            # todo log exception
            # todo 邮件告警
            print(f'# POST v1/score/user {i} connect to mysql failed: {e}')
            if i == 4:
                return False
            continue
        return db


def calculate_user_credit_scores_first_time(db, cur, cardID, user_data):
    """
        功能：用户第一次查询信用分
        param:
            db:
            cur:
            cardID:身份证号
            user_data：用户数据 todo 数据未知
    """
    print(f'ready to calculate  user credit_scores the first time {cardID}')
    user_scores = get_user_scores(user_data, 0, db, cur)
    if not user_scores:
        return
    sql = 'insert into user_credit_scores (uid,xm,basic_info,corporate,public_welfare,law,economic,life,created_time,updated_time,credit_score) values (%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s)'
    try:
        cur.execute(sql, [
            cardID,
            user_data.get('xm'),
            user_scores["basic_info"],
            user_scores["corporate"],
            user_scores["public_welfare"],
            user_scores["law"],
            user_scores["economic"],
            user_scores["life"],
            user_scores["credit_score"],
        ])
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"calculate user credit_score the first time failed:{cardID} : {e}")
        return
    return cardID


def update_user_credit_scores(db, cur, cardID, user_data, type_code):
    """
    功能：用户更新信用分
    param:
        db:
        cur:
        cardID:身份证号
        user_data：用户数据
        type_code：0：个人首次查询  1：个人更新  2：批量更新
    """
    print(f'ready to update user credit_scores {cardID}')
    user_scores = get_user_scores(user_data, type_code, db, cur)
    if not user_scores:
        return
    sql = 'update user_credit_scores set basic_info=%s,corporate=%s,public_welfare=%s,law=%s,economic=%s,life=%s,updated_time=now(),credit_score=%s where uid=%s'
    try:
        cur.execute(sql, [
            user_scores["basic_info"],
            user_scores["corporate"],
            user_scores["public_welfare"],
            user_scores["law"],
            user_scores["economic"],
            user_scores["life"],
            user_scores["credit_score"],
            cardID
        ])
        db.commit()
        print('updated scores successes')
    except Exception as e:
        print('xxxxxxxxxxx')
        db.rollback()
        print(f"update user credit_scores failed ：{cardID} :{e}")
        return
    return cardID


class ScoreView(View):

    def get(self, request):
        result = {
            "code": '1',
            'message': "请求不合法",
            'data': {}
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        """
        功能：单个用户查询信用分，计算或者更新
        param:
            cardID:身份证号
            name：姓名
        """
        json_str = request.body

        # 判断请求体是否为空
        if not json_str:
            result = {
                'code': '1',
                'message': '请求参数不合法',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

        json_obj = json.loads(json_str)
        cardID = str(json_obj.get('cardID'))
        name = str(json_obj.get('name'))
        print(11111)
        # 判断是否包含必要参数cardID & name
        if not cardID or not name:
            result = {
                "code": '1',
                'message': "请求参数缺失",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        print(22222)

        # 判断身份证格式
        try:
            re_result = re.findall('^\d{17}[0-9Xx]$', cardID)
            if not re_result:
                result = {
                    "code": '1',
                    'message': "身份证格式有误",
                    'data': {}
                }
                return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            print(e)

        print(f"# POST v1/score/user {cardID} is ready to calculate or update credit score")

        # 获取用户各项分数
        user_data = {
            "sfzh": cardID,
            "xm": name
        }

        # 连接数据库
        db = connect_mysql()
        if not db:
            result = {
                "code": '1',
                'message': "查询/计算分数数据库连接错误",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        cur = db.cursor()
        # 查询是否存在calculate_score_log_year_month 表,无则创建
        calculate_score_log_year_month(cur)
        # 查询是否为旧用户
        sql = 'select uid from user_credit_scores where uid=%s'
        try:
            cur.execute(sql, [cardID])
            print('execute select created_time-----------------')
        except Exception as e:
            # todo log
            print('error inquire user if is old failed because: %s' % e)
            result = {
                "code": '1',
                'message': "查询是否为旧用户失败",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

        select_result = cur.fetchone()
        if select_result:
            # 该用户为旧用户
            result = update_user_credit_scores(db, cur, cardID, user_data, 1)
            if result:
                result = {
                    "code": '0',
                    'message': "该用户信用分已更新完成",
                    'data': {}
                }
            else:
                result = {
                    "code": '1',
                    'message': "该用户信用分更新失败",
                    'data': {}
                }
            cur.close()
            db.close()
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        else:
            # 该用户为新用户
            result = calculate_user_credit_scores_first_time(db, cur, cardID, user_data)
            if result:
                result = {
                    "code": '0',
                    'message': "该用户信用分已计算完成",
                    'data': {}
                }
            else:
                result = {
                    "code": '1',
                    'message': "该用户信用分计算失败",
                    'data': {}
                }
            cur.close()
            db.close()
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


def calculate_score_log_year_month(cur):
    """
    查询是否存在calculate_score_log_year_month 表,无则创建
    """
    year = time.localtime()[0]
    month = time.localtime()[1]
    sql = 'show tables'
    cur.execute(sql)
    result = cur.fetchall()
    for i in result:
        print(i)
        if f'calculate_score_log_{year}_{month}' in i:
            print('本月日志表已存在')
            return f'calculate_score_log_{year}_{month}'
    try:
        sql = f"CREATE TABLE calculate_score_log_{year}_{month} (id int NOT NULL PRIMARY KEY AUTO_INCREMENT,uid char(18)  DEFAULT NULL COMMENT '身份证号',type tinyint(1)  DEFAULT NULL COMMENT '个人查询/个人更新/批量更新',status tinyint(1) DEFAULT NULL COMMENT '所有元件数据获取成功，设置为0',element varchar(128) DEFAULT NULL COMMENT '异常元件简称',reason varchar(256) DEFAULT NULL COMMENT '第三方接口异常原因',mission_time datetime DEFAULT NULL COMMENT '创建时间')"
        cur.execute(sql)
    except Exception as e:
        print(f'本月日志表创建失败    {e}')
        return False
    print('本月日志表创建成功')
    return f'calculate_score_log_{year}_{month}'


class MissionView(View):
    def get(self, request):
        result = {
            "code": 1,
            'message': "请求不合法",
            'data': {}
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        print(f'mission post from {request.META["REMOTE_ADDR"]}')
        json_str = request.body
        if not json_str:
            result = {
                'code': '1',
                'message': '请求参数不合法',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        json_obj = json.loads(json_str)
        mission = str(json_obj.get('mission', '1'))
        if not mission:
            result = {
                'code': '1',
                'message': '请求参数缺失',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        global mission_statu
        db = connect_mysql()
        if not db:
            result = {
                'code': '1',
                'message': '数据库连接失败',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        cur = db.cursor()
        # 获取用户总数
        sql = 'select max(id) from user_credit_scores'
        cur.execute(sql)
        users_count = cur.fetchone()[0]
        if not users_count:
            result = {
                'code': '1',
                'message': '数据库暂无用户',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        try:
            sql = 'select max(id) from mission_record_time'
            cur.execute(sql)
            result = cur.fetchone()[0]
            print(result)
        except Exception as e:
            print('mission_record_time  max(id) 查询失败')
            result = {
                'code': '1',
                'message': '数据库表mission_record_time查询失败',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        # 查询是否存在calculate_score_log_year_month 表,无则创建
        calculate_score_log_year_month(cur)
        # 第一次调度任务标记
        first = 0
        if result:
            print(result)
            max_id = result
            print(max_id)
            sql = 'select mission_time,statu from mission_record_time where id=(select max(id) from mission_record_time)'
            cur.execute(sql)
            result = cur.fetchone()
            mission_time = result[0]
            statu = result[1]
            print(statu)
            print(mission_time)
            print('不是第一次')
        else:
            first = 1
            mission_time = None
            print('第一次请求')
        if mission == '0':
            print(mission_statu)
            if mission_statu == 0:
                result = {
                    'code': '1',
                    'message': '任务正在执行中',
                    'data': {}
                }
                return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
            elif mission_statu == 2:
                result = {
                    'code': '0',
                    'message': '任务继续执行',
                    'data': {}
                }
                print('任务准备继续执行')
                mission_statu = 0
                mission_threading = Thread(target=start_mission, args=[mission_time, mission_statu, first,db,cur])
                mission_threading.start()
                print('任务继续执行')
                return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
            # sql = 'update mission_record_time set statu=%s where mission_time=%s'
            # cur.execute(sql, [0,mission_time])
            print('3')

            mission_threading = Thread(target=start_mission, args=[mission_time, mission_statu, first,db,cur])
            mission_threading.start()
            mission_statu = 0
            print('return success')
            result = {
                'code': '0',
                'message': '已开始任务',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        else:
            if mission_statu == 1:
                result = {
                    'code': '1',
                    'message': '任务未开始',
                    'data': {}
                }
            elif mission_statu == 2:
                result = {
                    'code': '1',
                    'message': '任务已被暂停，请勿重复提交',
                    'data': {}
                }
            else:
                # sql = 'update mission_record_time set statu=%s where id=(select max(id) from mission_record_time)'
                # cur.execute(sql, [1])
                mission_statu = 2
                result = {
                    'code': '0',
                    'message': '已暂停成功',
                    'data': {}
                }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


def start_mission(mission_time, statu, first,db, cur):
    """
    调度任务开始
    """
    print('调度任务开始')
    # 获取用户总数
    sql = 'select max(id) from user_credit_scores'
    cur.execute(sql)
    users_count = cur.fetchone()[0]
    if not users_count:
        result = {
            'code': '1',
            'message': '数据库暂无用户',
            'data': {}
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    print("users_count")
    print(users_count)
    mission_config = conf['mission']
    update_credit_score_quantity = int(mission_config.get('update_credit_score_quantity', 1000))
    if users_count <= update_credit_score_quantity:
        update_one_time_quantity = 2
    else:
        update_one_time_quantity = update_credit_score_quantity
    # 循环 批量获取数据
    print("begin")
    global mission_statu
    print(mission_statu)
    for i in range(1, users_count, update_one_time_quantity):
        if mission_statu == 0:
            # 获取开始到结束的批量用户
            if first == 1:
                sql = 'select id,uid,xm from user_credit_scores where id between %s and %s and updated_time<now()'
                cur.execute(sql, [i, i + update_one_time_quantity])
                print(" first == 1")
            else:
                print(" first != 1")
                sql = 'select id,uid,xm from user_credit_scores where id between %s and %s and updated_time<'
                sql += '(select mission_time from mission_record_time ORDER BY id DESC limit 1)'
                cur.execute(sql, [i, i + update_one_time_quantity])
            users = cur.fetchall()
            print(users)
            for user in users:
                user_data = {
                    "sfzh": user[1],
                    "xm": user[2]
                }
                time.sleep(0.1)
                update_user_credit_scores(db, cur, user[1], user_data, 2)
        elif mission_statu == 2:
            # 停止任务
            return
    # sql = 'select mission_time,statu from mission_record_time where id=(select max(id) from mission_record_time)'
    # cur.execute(sql)
    # result = cur.fetchone()[0]
    # print(result)
    # mission_time = result[0]
    # sql = 'update mission_record_time set statu=%s where mission_time=%s '
    # cur.execute(sql, [1, mission_time])
    time.sleep(1)
    try:
        sql = 'select max(id) from mission_record_time'
        cur.execute(sql)
        max_id = cur.fetchone()[0]
        print(max_id)
        sql = 'update mission_record_time set statu=1 where id=%s'
        cur.execute(sql, [max_id])
        print("success")
        sql = 'select statu from mission_record_time ORDER BY id DESC limit 1'
        cur.execute(sql)
        statu = cur.fetchone()[0]
        print(statu)
        db.commit()
    except:
        print("update mission_record_time set statu=1  failed")
        db.rollback()
    mission_statu = 1
    print(mission_statu)
    return
