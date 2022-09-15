"""
德阳市市民数据元件获取工具
@author:willow918@163.com
version:220908
created_time:2022-09-08
description:可通过调用类方法向 中国电子数据流通平台 获取市民相关数据元件信息
"""
import requests
import json
from urllib import parse
import redis

# 元件api地址
element_api_url = 'http://222.213.125.95:8081/dc-dbapi/api/getApi'

element_appkey_id = {
    "德阳市职工婚姻登记状态数据元件": ("", "164819098898223"),
    "德阳市职工社保缴费状态数据元件": ("", ""),
    "德阳市职工社保累计缴纳月份数数据元件": ("63cba0b30cf0aca74782d188f9b307af", "164670660220556"),
    "德阳市职工社保缴费单位性质数据元件": ("3e486cc7b222ccf8901c36fc43066eae", "164670499149768"),
    "德阳市执行失信名单个人失信状态数据元件": ("daaf1d874747f5f1acb6b9d3a9cd6962", "165465633238698"),
    "德阳市信用专利信息数据元件": ("", ""),
    "德阳市税务局处罚结果数据元件": ("", ""),
    "德阳市失信黑名单与守信红名单查询数据元件": ("", "")
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
        self.url = 'http://222.213.125.95:8081/dc-sso/componentToken/generateAppToken'
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
        data = json.dumps(data)
        try:
            data = requests.post(url=self.url, headers=headers, data=data, timeout=self.timeout).json()
        except Exception as e:
            # TODO: log
            pass

        """
        返回结果示例  
        {
        "code": 200,
        "message": "操作成功",
        "data": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1VzZXJfbmFtZSI6IjE3M......"
        }
        """
        if data['code'] == 200:
            return data["data"]
        else:
            return None


class Element(Elements):

    def __init__(self, appkey=None, id=None, pagesize=None, pageno=None, sfzh=None, xm=None, gzdwxz=None,
                 jfljnxqj=None, ):
        """

        :param appkey: 已完成订单appkey
        :param id:元件API id
        :param pagesize:分页查询参数，每页多少条数据
        :param pageno:分页查询参数，第几页
        :param sfzh:身份证号
        :param xm:姓名
        :param gzdwxz:工作单位性质
        :param jfljnxqj:社保缴费累计年限区间
        """
        super().__init__()
        self.appkey = appkey
        self.redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)
        self.id = id
        self.query = {
            "appkey": appkey,
            "pageSize": pagesize,
            "pageNo": pageno,
            # "sfzh": sfzh,
            # "xm": xm,
            # "gzdwxz": gzdwxz,
            # "jfljnxqj": jfljnxqj
        }

    # http://222.213.125.95:8081/dc-dbapi/api/getApi164***********?sfzh=*****&xm=***&pageSize=20&pageNo=1
    def get_element_data(self):
        """"""
        url = element_api_url + self.id + '?' + parse.urlencode(self.query)
        app_token = self.redis_connection.get(self.appkey)
        if not app_token:
            for i in range(5):
                app_token = super().get_app_token(self.appkey)
                if app_token:
                    break
                else:
                    if i == 4:
                        # TODO log
                        return None
                    continue
            self.redis_connection.set(self.appkey, app_token, 300)
        else:
            app_token = app_token.decode()
        headers = {
            "app-token": app_token
        }
        data = None
        try:
            data = requests.get(url=url, headers=headers, timeout=1).json()
        except Exception as e:
            # TODO: log
            pass
        return data

    @staticmethod
    def get_marriage_state(data: dict):
        """
        获取 德阳市职工婚姻登记状态数据元件 婚姻状态
        反映1960至1996年出生职工的婚姻状态，无输出信息可认定为未婚；（查询人年龄=1960至1996年）
        婚姻状态：1-已婚，2-离异
        :param data:user_info
        :return:lx:varchar
        """
        data['appkey'] = element_appkey_id["德阳市职工婚姻登记状态数据元件"][0]
        data['id'] = element_appkey_id["德阳市职工婚姻登记状态数据元件"][1]
        data['pagesize'] = 20
        data['pageno'] = 1
        data['xm'] = None
        data['sfzh'] = None
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_social_security_payment_months(data: dict):
        """
        获取 德阳市职工社保累计缴纳月份数数据元件 社保缴费累计年限区间
        通过查询职工社保缴费累计月份数，反映社保缴费年限区间（半年以内，半年至一年，一年至三年，三年至五年，五年至十年，十年以上）
        :param data:user_info
        :return:jfljnxqj:varchar
        """
        data['appkey'] = element_appkey_id["德阳市职工社保累计缴纳月份数数据元件"][0]
        data['id'] = element_appkey_id["德阳市职工社保累计缴纳月份数数据元件"][1]
        data['pagesize'] = 20  # 必填
        data['pageno'] = 1  # 必填
        data['xm'] = None
        data['sfzh'] = None
        data['jfljnxqj'] = None  # 必填
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_unit_nature(data: dict):
        """
        获取 德阳市职工社保缴费单位性质数据元件 工作单位性质
        通过查询企业行政级别分类反映职工工作单位性质（企业、政府机构、政府单位、事业团体）
        :param data:user_info
        :return:gzdwxz:varchar
        """
        data['appkey'] = element_appkey_id["德阳市职工社保缴费单位性质数据元件"][0]
        data['id'] = element_appkey_id["德阳市职工社保缴费单位性质数据元件"][1]
        data['pagesize'] = 20   # 必填
        data['pageno'] = 1  # 必填
        # data['xm'] = None
        # data['sfzh'] = None
        # data['gzdwxz'] = None
        element = Element(**data)
        return element.get_element_data()

    @staticmethod
    def get_personal_dishonesty_state(data: dict):
        """
        获取 德阳市执行失信名单个人失信状态数据元件  失信状态
        姓名/名称,证件号码,立案时间,发布时间,状态,屏蔽时间,撤销时间,失信到期日,失信行为情形
        :param data:user_info
        :return:xm:varchar,sfsx:varchar
        """
        data['appkey'] = element_appkey_id["德阳市执行失信名单个人失信状态数据元件"][0]
        data['id'] = element_appkey_id["德阳市执行失信名单个人失信状态数据元件"][1]
        data['pagesize'] = 20
        data['pageno'] = 1
        data['sfzh'] = None
        element = Element(**data)
        return element.get_element_data()


data = Element.get_unit_nature({})
print(data)
# data = Element.get_social_security_payment_months({})
print(data)
# data = Element.get_personal_dishonesty_state({})
print(data)
