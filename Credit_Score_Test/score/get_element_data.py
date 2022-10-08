"""
德阳市市民数据元件获取工具
@author:willow918@163.com
version:220908
created_time:2022-09-08
description:可通过调用类方法向 中国电子数据流通平台 获取市民相关数据元件信息
"""
import os
import configparser
import random
import time

import requests
import json
from urllib import parse
import redis

from algorithm.calculate_user_scores import calculate_user_scores

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

# 元件api地址
element_api_url = 'http://59.213.91.96:80/dc-dbapi/api/getApi'

element_appkey_id = {
    "德阳市职工婚姻登记状态数据元件": ("", "164819098898223"),
    "德阳市职工社保缴费状态数据元件": ("", ""),
    "德阳市职工社保累计缴纳月份数数据元件": ("63cba0b30cf0aca74782d188f9b307af", "164670660220556"),
    "德阳市职工社保缴费单位性质数据元件": ("3e486cc7b222ccf8901c36fc43066eae", "164670499149768"),
    "德阳市执行失信名单个人失信状态数据元件": ("daaf1d874747f5f1acb6b9d3a9cd6962", "165465633238698"),
    "德阳市信用专利信息数据元件": ("", ""),
    "德阳市税务局处罚结果数据元件": ("", ""),
    "德阳市失信黑名单与守信红名单查询数据元件": ("b4612cf1dfbe8cd0b4e6fdff143fe311", "165310702467054")
}


class Elements:
    def __init__(self):
        """
        phone:中国电子数据流通平台 账户
        password:中国电子数据流通平台 密码
        url:apptoken获取地址
        """
        self.phone = '13281834377'
        self.password = '123456'
        self.url = 'http://59.213.91.96:80/dc-sso/componentToken/generateAppToken'
        self.timeout = 1

    def get_app_token(self, appkey):
        """
        获取某元件对应的apptoken
        :param appkey: 中国电子数据流通平台-已完成订单-元件信息-appkey
        :return: apptoken
        """
        headers = {'Content-Type': 'application/json'}
        data = {
            'appkey': appkey,
            'input': self.phone,
            'password': self.password
        }
        try:
            data = requests.post(url=self.url, headers=headers, json=data, timeout=self.timeout).json()
        except Exception as e:
            # TODO: log
            print(f"post {appkey} failed!!!!!!!")
            # 获取app_token失败 登录信息有误
            # TODO
            return
        """
        返回结果示例  
        {
        "code": 200,
        "message": "操作成功",
        "data": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1VzZXJfbmFtZSI6IjE3M......"
        }
        """
        # 判断返回结果分类
        if "code" in data.keys():
            if data['code'] == 200:
                return data['data']
            else:
                # 获取app_token失败 登录信息有误
                return
        else:
            # 获取app_token失败 登录信息有误
            return


class Element(Elements):

    def __init__(self, appkey=None, id=None, pagesize=None, pageno=None, sfzh=None, xm=None, gzdwxz=None,
                 jfljnxqj=None, qygtgshmc=None):
        """

        :param appkey: 已完成订单appkey
        :param id:元件API id
        :param pagesize:分页查询参数，每页多少条数据
        :param pageno:分页查询参数，第几页
        :param sfzh:身份证号
        :param xm:姓名
        :param gzdwxz:工作单位性质
        :param jfljnxqj:社保缴费累计年限区间
        :param qygtgshmc:企业/个体工商户名称
        """
        super().__init__()
        self.appkey = appkey
        if redis_config["PASSWORD"] == "None":
            self.redis_connection = redis.Redis(host=redis_config["HOST"], port=int(redis_config["PORT"]), db=0)
        else:
            self.redis_connection = redis.Redis(host=redis_config["HOST"], port=int(redis_config["PORT"]),
                                                password=redis_config["PASSWORD"], db=0)
        self.id = id
        self.query = {
            "appkey": appkey,
            "pageSize": pagesize,
            "pageNo": pageno,
        }
        if sfzh:
            self.query["sfzh"] = sfzh
        else:
            pass
        if xm:
            self.query["xm"] = xm
        else:
            pass
        if gzdwxz:  # 工作单位性质
            self.query["gzdwxz"] = gzdwxz
        else:
            pass
        if jfljnxqj:  # 社保缴费累计年限区间
            self.query["jfljnxqj"] = jfljnxqj
        else:
            pass
        if qygtgshmc:
            self.query["qygtgshmc"] = qygtgshmc
        else:
            pass
        # print(self.query)

    # http://59.213.91.96:80/dc-dbapi/api/getApi164***********?sfzh=*****&xm=***&pageSize=20&pageNo=1
    def get_element_data(self):
        """"""
        url = element_api_url + self.id + '?' + parse.urlencode(self.query)
        app_token = self.redis_connection.get(self.appkey)
        if not app_token:
            for i in range(4):
                app_token = super().get_app_token(self.appkey)
                if app_token:
                    self.redis_connection.set(self.appkey, app_token, 3000)
                    break
                else:
                    if i == 3:
                        print(f'get_app_token id:{self.id} failed ')
                        # TODO raise exception
                        # TODO 暂时返回 0
                        return 0
                    continue
        else:
            app_token = app_token.decode()
        headers = {
            "app-token": app_token
        }
        # TODO 判断token是否过期
        data = 0
        try:
            # TODO timeout?
            data = requests.get(url=url, headers=headers).json()
        except Exception as e:
            # TODO: log
            print(f"{self.id} get_element_data failed")
        if data:
            return data
        else:
            return 0

    @staticmethod
    def get_marriage_state(user_data: dict):
        """
        获取 德阳市职工婚姻登记状态数据元件 婚姻状态
        反映1960至1996年出生职工的婚姻状态，无输出信息可认定为未婚；（查询人年龄=1960至1996年）
        婚姻状态：1-已婚，2-离异
        :query param data:user_info
        :return:lx:varchar
        """
        data = {
            'appkey': element_appkey_id["德阳市职工婚姻登记状态数据元件"][0],
            'id': element_appkey_id["德阳市职工婚姻登记状态数据元件"][1],
            'pagesize': 20,
            'pageno': 1,
            'xm': user_data['xm'],
            'sfzh': user_data['sfzh']
        }
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_social_security_payment_months(user_data: dict):
        """
        获取 德阳市职工社保累计缴纳月份数数据元件 社保缴费累计年限区间
        通过查询职工社保缴费累计月份数，反映社保缴费年限区间（半年以内，半年至一年，一年至三年，三年至五年，五年至十年，十年以上）
        :query param data:user_info
        :return:jfljnxqj:varchar
        """
        data = {
            'appkey': element_appkey_id["德阳市职工社保累计缴纳月份数数据元件"][0],
            'id': element_appkey_id["德阳市职工社保累计缴纳月份数数据元件"][1],
            'pagesize': 1,
            'pageno': 1,
            'xm': user_data.get('xm')
        }
        # TODO 根据用户身份证查询姓名 的函数
        print(data['xm'])
        data['sfzh'] = user_data['sfzh']
        # data['jfljnxqj'] = "十年以上"  # 必填
        '''
        十年以上
        五年至十年
        三年至五年
        一年至三年
        半年至一年
        半年以内
        '''
        element = Element(**data)
        result = element.get_element_data()
        print('德阳市职工社保累计缴纳月份数数据元件',end='    ')
        print(result)
        try:
            result = result['data'][0]["jfljnxqj"]
            if result == "十年以上":
                return 5
            if result == "五年至十年":
                return 4
            if result == "三年至五年":
                return 3
            if result == "一年至三年":
                return 2
            if result == "半年至一年":
                return 1
            if result == "半年以内":
                return 0
            else:
                return "None"
        except:
            return 'None'

    @staticmethod
    def get_unit_nature(user_data: dict):
        """
        获取 德阳市职工社保缴费单位性质数据元件 工作单位性质
        通过查询企业行政级别分类反映职工工作单位性质（企业、政府机构、政府单位、事业团体）
        :query param data:user_info
        :return:gzdwxz:varchar
        """
        data = {
            'appkey': element_appkey_id["德阳市职工社保缴费单位性质数据元件"][0],
            'id': element_appkey_id["德阳市职工社保缴费单位性质数据元件"][1],
            'pagesize': 1, 'pageno': 1,
            'xm': user_data['xm'],
            'sfzh': user_data['sfzh']
        }
        # data['gzdwxz'] = None
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_personal_dishonesty_state(user_data: dict):
        """
        获取 德阳市执行失信名单个人失信状态数据元件  失信状态
        姓名/名称,证件号码,立案时间,发布时间,状态,屏蔽时间,撤销时间,失信到期日,失信行为情形
        :query param data:user_info
        :return:xm:varchar,sfsx:varchar
        """
        data = {
            'appkey': element_appkey_id["德阳市执行失信名单个人失信状态数据元件"][0],
            'id': element_appkey_id["德阳市执行失信名单个人失信状态数据元件"][1],
            'pagesize': 1,
            'pageno': 1,
            'sfzh': user_data['sfzh']}
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_black_and_red_list(user_data: dict):
        """
        获取 德阳市失信黑名单与守信红名单查询数据元件  失信状态
        姓名/名称,证件号码,立案时间,发布时间,状态,屏蔽时间,撤销时间,失信到期日,失信行为情形
        :query param pagesize:int 分页查询参数，每页多少条数据
        :query param pageno:int   分页查询参数，第几页
        :query param data:dict    user_info
        :query param qygtgshmc:varchar    企业/个体工商户名称
        :return:
            hhmdlx:varchar  红黑名单类型
            fbsj:varchar    发布时间
        """
        data = {
            'appkey': element_appkey_id["德阳市失信黑名单与守信红名单查询数据元件"][0],
            'id': element_appkey_id["德阳市失信黑名单与守信红名单查询数据元件"][1],
            'pagesize': 1,
            'pageno': 1,
            'qygtgshmc': user_data['qygtgshmc']
        }
        element = Element(**data)
        return element.get_element_data()


user_list = [
    {'sfzh': '510623198009210017', 'xm': '刘辉'},
    # {'sfzh': '510603198511186678', 'xm': '唐龑'},
    # {'sfzh': '510622199608195718', 'xm': '何颖'},
    # {'sfzh': '510625199507110016', 'xm': '郭朋鑫'},
    # {'sfzh': '510723199804070017', 'xm': '胡笛潇'},
    # {'sfzh': '510603199303110303', 'xm': '杨春桃'},
    # {'sfzh': '510603199702240985', 'xm': '邓雨桐'},
    # {'sfzh': '500229199510210220', 'xm': '周付琴'},
    # {'sfzh': '510682198512240029', 'xm': '曾潇潇'},
    # {'sfzh': '510723199705030044', 'xm': '贾丽莎'},
    # {'sfzh': '510603198701115969', 'xm': '李仁可'},
    # {'sfzh': '510682198707070031', 'xm': '赖韬'},
    # {'sfzh': '510682198607010525', 'xm': '边明思'},
    # {'sfzh': '510602199606227661', 'xm': '朱航'},
    # {'sfzh': '510602197601261693', 'xm': '曾振金'},
    # {'sfzh': '511025197309216791', 'xm': '周龙生'},
    # {'sfzh': '513721199009081008', 'xm': '张又杉'},
    # {'sfzh': '51060319931108783X', 'xm': '邓杰堃'},
    # {'sfzh': '510603199705095939', 'xm': '邱奕铭'},
    # {'sfzh': '510622199510103010', 'xm': '董永亮'},
    # {'sfzh': '510623199606040815', 'xm': '龚荣志'},
    # {'sfzh': '510722199401270026', 'xm': '曾小苡'},
    # {'sfzh': '510622199508123012', 'xm': '牟小虎'},
    # {'sfzh': '51068320000831091X', 'xm': '杜沛霖'},
    # {'sfzh': '510603198710262047', 'xm': '罗琛'},
    # {'sfzh': '510623199606292115', 'xm': '满光东'},
    # {'sfzh': '510681199908230319', 'xm': '廖朗迅'},
    # {'sfzh': '510683200105220027', 'xm': '梅筱璐'},
    # {'sfzh': '141034199606110068', 'xm': '王舒婷'},
    # {'sfzh': '510603198602056502', 'xm': '肖燕燕'},

]

company_list = [
    {"qygtgshmc": "德阳鑫锐科技有限公司"},
    {"qygtgshmc": "工赋（德阳）科技有限公司"},
    {"qygtgshmc": "百度"},
    {"qygtgshmc": "德阳市南天科技有限公司"},
    {"qygtgshmc": "德阳市恒志科技有限公司"},
    {"qygtgshmc": "德阳鼎宏科技有限责任公司"},
]

for i in user_list:
    # data = Element.get_unit_nature(i)
    # print(data)
    # data = Element.get_social_security_payment_months(i)
    # print(data)
    # data = Element.get_personal_dishonesty_state(i)
    # print(data)
    pass

for item in company_list:
    # data = Element.get_black_and_red_list(i)
    # print(data)
    pass

# def calculate_user_scores(user_indexs: dict):
#     """
#     随机模拟分数
#     """
#     user_scores = {}
#     # TODO 根据指标计算用户信用分数
#     user_scores["basic_info"] = random.randint(550, 600),
#     user_scores["corporate"] = 0,
#     user_scores["public_welfare"] = random.randint(500, 550),
#     user_scores["law"] = 1000,
#     user_scores["economic"] = random.randint(650, 700),
#     user_scores["life"] = 800,
#     user_scores["credit_score"] = random.randint(700, 800),
#     return user_scores
