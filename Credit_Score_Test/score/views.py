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
import pymysql
import re
from .get_element_data import get_user_scores
import configparser
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('myconfig.ini', 'w', encoding="utf-8") as f:
    with open(BASE_DIR + '/config.ini', 'r', encoding="utf-8") as con_f:
        f.write(con_f.read())
conf = configparser.ConfigParser()
conf.read('myconfig.ini', encoding="utf-8")
envi_config = conf['envi']
envi=envi_config.get('envi','local')
mysql_config=conf[envi + '_mysql']
redis_config = conf[envi + '_redis']
mission_config = conf['mission']
update_credit_score_quantity = mission_config.get('update_credit_score_quantity', 1000)

mission_statu = 0


def connect_mysql():
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


def caculate_user_credit_scores_first_time(db, cur, cardID, user_data):
    """
        功能：用户第一次查询信用分
        param:
            db:
            cur:
            cardID:身份证号
            user_data：用户数据 todo 数据未知
    """
    print(f'ready to caculate  user credit_scores the first time {cardID}')
    user_scores = get_user_scores(user_data)
    sql = 'insert into user_credit_scores (uid,basic_info,corporate,public_welfare,law,economic,life,created_time,updated_time,credit_score) values (%s,%s,%s,%s,%s,%s,%s,now(),now(),%s)'
    try:
        cur.execute(sql, [
            cardID,
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
        print(f"cuculate user credit_score the first time failed:{cardID} : {e}")
        return
    return cardID


def update_user_credit_scores(db, cur, cardID, user_data):
    """
    功能：用户更新信用分
    param:
        db:
        cur:
        cardID:身份证号
        user_data：用户数据 todo 数据未知
    """
    print(f'ready to update user credit_scores {cardID}')
    user_scores = get_user_scores(user_data)
    sql = 'update user_credit_scores set basic_info=%s,corporate=%s,public_welfare=%s,law=%s,economic=%s,life=%s,updated_time=now(),credit_score=%s where uid=%s'
    print('get scores successed')
    try:
        print('get scores successed')
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
        print('get scores successed')
        db.commit()
        print('updated scores successed')
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
        功能：单个用户查询信用分
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
        cardID = json_obj.get('cardID')
        name = json_obj.get('name')
        # 判断是否包含必要参数cardID & name
        if not cardID or not name:
            result = {
                "code": '1',
                'message': "请求参数缺失",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

        # 判断身份证格式
        re_result = re.findall('^\d{17}[0-9Xx]$', cardID)
        if not re_result:
            result = {
                "code": '1',
                'message': "身份证格式有误",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

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
            result = update_user_credit_scores(db, cur, cardID, user_data)
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
            result = caculate_user_credit_scores_first_time(db, cur, cardID, user_data)
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
        mission = json_obj.get('mission', '1')
        if not mission:
            result = {
                'code': '1',
                'message': '请求参数缺失',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        global mission_statu
        if mission == '0':
            mission_statu = 0
            result = start_mission()
            if result == '数据库连接失败':
                result = {
                    'code': '1',
                    'message': '开始任务数据库连接失败',
                    'data': {}
                }
            else:
                result = {
                    'code': '0',
                    'message': '开始任务执行成功',
                    'data': {}
                }
        else:
            mission_statu = 1
            result = {
                'code': '0',
                'message': '暂停任务执行成功',
                'data': {}
            }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


def start_mission():
    """
    调度任务开始
    """
    # 创建mysql connect
    db = connect_mysql()
    if not db:
        return '数据库连接失败'
    cur = db.cursor()

    # 获取用户总数
    sql = 'select count(uid) from user_credit_sco?res where updated_time>curdate()'
    sql = 'select max(id) from user_credit_scores'
    cur.execute(sql)
    users_count = cur.fetchone()[0]
    mission_config = conf['mission']
    update_credit_score_quantity = int(mission_config.get('update_credit_score_quantity', 1000))
    if users_count <= update_credit_score_quantity:
        update_one_time_quantity = 1
    else:
        update_one_time_quantity = update_credit_score_quantity
    # 循环 批量获取数据
    for i in range(1, users_count, update_one_time_quantity):
        if mission_statu == 0:
            # 获取开始到结束的批量用户
            sql = 'select id,uid from user_credit_scores where id between %s and %s and updated_time<now()'
            cur.execute(sql, [i, i + update_one_time_quantity])
            users = cur.fetchall()
            for user in users:
                user_data={"sfzh":user[1]}
                time.sleep(0.1)
                update_user_credit_scores(db, cur, user[1],user_data)
        elif mission_statu == 1:
            # 停止任务
            cur.close()
            db.close()
            return
    cur.close()
    db.close()
    return 1
