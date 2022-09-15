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

mission_statu = 0


class ScoreView(View):

    def get(self, request):
        result = {
            "code": '1',
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        """
        功能：单个用户查询信用分
        param:
            cardID:身份证号
            name：姓名 todo 不一定需要姓名
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

        # 判断是否包含必要参数cardID name
        if not cardID or not name:
            result = {
                "code": '1',
                'message': "请求参数错误",
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

        # todo log search record
        print(f"# POST v1/score/user {re_result} is ready to calculate or update credit score")

        # 连接数据库
        for i in range(5):
            try:
                db = pymysql.connect(
                    host="localhost",
                    port=3306,
                    user="root",
                    password="123456",
                    database="credit_score",
                    charset="utf8")
            except Exception as e:
                # todo log exception
                # todo 邮件告警
                print(f'# POST v1/score/user {i} connect to mysql failed: {e}')
                if i == 4:
                    result = {
                        "code": '1',
                        'message': "数据库连接错误",
                        'data': {}
                    }
                    return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
                continue
            break
        cur = db.cursor()
        sql = 'select uid from user_credit_scores where uid=%s'

        # 查询是否为旧用户
        try:
            cur.execute(sql, [cardID])
            print('execute select created_time-----------------')
        except Exception as e:
            # todo log
            # todo 邮件告警
            print('error 查询是否为旧用户: %s' % e)
            result = {
                "code": '1',
                'message': "查询是否为旧用户失败",
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        select_result = cur.fetchone()
        if select_result:
            # 该用户为旧用户
            # todo 计算分数
            print(f'execute select created_time success  ')
            sql = 'update user_credit_scores set basic_info=%s,corporate=%s,public_welfare=%s,law=%s,economic=%s,life=%s,updated_time=%s,credit_score=%s where uid=%s'
            try:
                cur.execute(sql, [
                    random.randint(6000, 7000),
                    random.randint(1500, 2000),
                    random.randint(3000, 4000),
                    random.randint(3000, 4000),
                    random.randint(5000, 6000),
                    random.randint(2000, 2600),
                    time.strftime('%y-%m-%d %H:%M:%S'),
                    random.randint(500, 800),
                    cardID
                ])
                db.commit()
            except Exception as e:
                print('error: %s' % e)
                db.rollback()
                cur.close()
                db.close()
                print("更新用户信用分是失败 %s" % e)
                result = {
                    "code": '1',
                    'message': "该用户信用分更新失败",
                    'data': {}
                }
                return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
            result = {
                "code": '0',
                'message': "该用户信用分已更新完成",
                'data': {}
            }
        else:
            # 该用户为新用户
            # todo 计算分数
            created_time = time.strftime('%y-%m-%d %H:%M:%S')
            sql = 'insert into user_credit_scores values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            try:
                cur.execute(sql, [
                    cardID,
                    random.randint(6000, 7000),
                    random.randint(1500, 2000),
                    random.randint(3000, 4000),
                    random.randint(3000, 4000),
                    random.randint(5000, 6000),
                    random.randint(2000, 2600),
                    created_time,
                    time.strftime('%y-%m-%d %H:%M:%S'),
                    random.randint(500, 800),
                ])
                db.commit()
            except Exception as e:
                db.rollback()
                cur.close()
                db.close()
                print("插入用户信用分是失败 %s" % e)
                result = {
                    "code": '1',
                    'message': "该用户信用分计算失败",
                    'data': {}
                }
                return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
            result = {
                "code": '0',
                'message': "该用户信用分已计算完成",
                'data': {}
            }
        cur.close()
        db.close()
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


class ScoresView(View):

    def get(self, request):
        result = {
            "code": '1',
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        result = {
            "code": '1',
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


class MissionView(View):
    def get(self, request):
        result = {
            "code": 1,
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})

    # def post(self, request):
    #     r = redis.Redis(host='127.0.0.1', port=6379, db=0, password='')
    #     mission_id = str(time.time())
    #     r.set(mission_id, 0)
    #     mission_status = 'mission_status'
    #     job = []
    #     for i in range(100):
    #         t = Thread(target=caculate, args=(i, r, mission_id, mission_status))
    #         t.daemon = True
    #         job.append(t)
    #     for i in job:
    #         i.start()
    #     data = {
    #         "code": 200,
    #         'message': "批量计算任务正在进行中",
    #         "mission_id": mission_id,
    #     }
    #     return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

    def post(self, request):
        print('mission post ----------------------------')
        json_str = request.body
        print(json_str)
        if not json_str:
            result = {
                'code': '1',
                'message': '请求参数不合法',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        json_obj = json.loads(json_str)
        mission = json_obj.get('mission')
        if not mission:
            result = {
                'code': '1',
                'message': '请求参数不合法',
                'data': {}
            }
            return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        if mission == '0':
            result = {
                'code': '0',
                'message': '开始任务执行成功',
                'data': {}
            }
            # todo 执行计算任务
            start_mission()
        else:
            result = {
                'code': '0',
                'message': '暂停任务执行成功',
                'data': {}
            }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


def test(request):
    if request.method == "GET":
        result = {
            "code": '1',
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    if request.method == "POST":
        result = {
            "code": '1',
            'message': "请求不合法"
        }
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})


# def caculate(i, r, mission_id, mission_status):
#     result=r.incr(mission_id)

def start_mission():
    """

    """
    #创建mysql connect

    #循环 批量获取数据
    #多线程
    #   判断mission_statu
    #   计算信用分
    #   插入信用分
