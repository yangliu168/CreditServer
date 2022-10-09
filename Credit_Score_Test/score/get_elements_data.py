"""
元件临时接口调用工具
@author:willow918@163.com
version:220929
created_time:2022-09-29
description:可通过调用类方法向 中国电子数据流通平台 获取市民相关数据元件信息
"""
import requests
import time
import urllib3
from urllib import parse

from .algorithm.calculate_user_scores import calculate_user_scores
from get_element_data import Element

# 忽略警告
urllib3.disable_warnings()

element_indexname_apiToken_path = {
    # 是否具有教师资格证
    # A3_02_03
    "绵竹市-根据姓名查询教师资格认证信息": {
        "indexname": "A3_02_03",
        "apiToken": "7966338e35d3406db7433db288c3d254",
        "path": "mzs/gjxmcxjszgrzxx?"
    },
    "什邡市-根据姓名查询教师资格认定合格信息": {
        "indexname": "A3_02_03",
        "apiToken": "c682bde8ddd74758abfec3f359589732",
        "path": "sfs/gjxmcxjszgrdhgxx?"
    },
    "旌阳区-根据身份证查询教师资格认定合格人员信息": {
        "indexname": "A3_02_03",
        "apiToken": "a799aae6fccf42cbb8bb3a56a4316426",
        "path": "jyq/gjsfzhcxjszgrzhgryxx?"
    },
    "广汉市-教师资格认定人员名册": {
        "indexname": "A3_02_03",
        "apiToken": "afc3664543ab4faaa273d244ca892b33",
        "path": "ghs/jszgrdrymc?"
    },

    # 是否具有导游资格
    # A3_02_02
    "市文旅局-根据身份证查询德阳市导游资格信息": {
        "indexname": "A3_02_02",
        "apiToken": "bcc3ad3f505845a6a4a0834a029be3ca",
        "path": "swlj/gjsfzcxdysdyzgxx?"
    },

    # 是否具有律师执业资格
    # A3_02_01
    "市司法局-根据身份证查询律师执业信息": {
        "indexname": "A3_02_01",
        "apiToken": "028fa13098dc48c9984802c6983a5ce2",
        "path": "ssfj/gjsfzcxlszyxx?"
    },

    # 个人被抵押房产数量
    # C1_03_02
    "市自然资源局-根据身份证号查询个人抵押信息": {
        "indexname": "C1_03_02",
        "apiToken": "26c72234c1b647dfa8984e6687882d35",
        "path": "zrzyj/gjsfzhcxgrdyxx?"
    },

    # 个人房产数量
    # C1_03_01
    # TODO POST
    "市住建局-德阳市根据买方身份信息获取存量房合同": {
        "indexname": "C1_03_01",
        "apiToken": "115305536eb2486a88e1198b711aadcf",
        "path": "szjj/gjmfsfxxhqclfht"
    },

    # 近5年被列入失信被执行人的次数
    # D2_01_01
    "发改委-失信被执行人名单信息": {
        "indexname": "D2_01_01",
        "apiToken": "ea1ae87537134ceb86af74647ae67382",
        "path": "fgw/sxbzxrmdxx?"
    },
    "市发改委-失信被执行人名单信息": {
        "indexname": "D2_01_01",
        "apiToken": "ea1ae87537134ceb86af74647ae67382",
        "path": "fgw/sxbzxrmdxx?"
    },
    # TODO
    # 市发改委-失信被执行人信息    接口    已申请

    # 近5年被行政处罚的次数
    # D1_01_01
    "市发改委-根据自然人身份证号码查询行政处罚信息": {
        "indexname": "D1_01_01",
        "apiToken": "18455f298bc04b0ca3a3936d8bcfdb53",
        "path": "sfgw/gjsfzhmcxzrrxzcfxx2?"
    },

    # 近5年获得省级荣誉的次数
    # E2_02_03
    # 近5年获得国家级荣誉的次数
    # E2_02_04
    # 近5年获得市级荣誉的次数
    # E2_02_02
    # 近5年获得县（区）级荣誉的次数
    # E2_02_01
    "市自然资源局-根据身份证号码查询德阳市自然人表彰信息": {
        "indexname": "E2_02_03",
        "apiToken": "3594b97a71a9406c81e92eaff3ebe308",
        "path": "zrzyj/gjsfzhmcxdyszrrbzxx?"
    },

}


class TemporaryElements:
    """
    临时接口父类
    """

    def __init__(self, ):
        self.query = {
            "pageNum": 1,
            "pageSize": 10,
            "appCode": self.get_appCode(),
            "qqfyyId": 'test',
            "qqfyymc": 'test',
            "qqrId": 'test',
            "qqr": 'test',
        }

    # 获取appCode
    @staticmethod
    def get_appCode():
        appId = "84247F0E39C54292907674C879033A78"
        appName = "DExchange"
        timeStamp = str(time.time())[0:8]
        appCode_url = f'https://59.213.91.249/exchangegateway/appauth/getappid?appId={appId}&appName={appName}&timeStamp={timeStamp}'
        try:
            # 取消验证
            appCode = requests.get(url=appCode_url, verify=False).json()["data"]
            return appCode
        except Exception as e:
            print(e)
            print(f'获取appCode失败{e}')
            return


class TemporaryElement(TemporaryElements):
    """
    临时接口子类
    """

    def __init__(self, apiToken=None, zjhm=None, sfzh=None, dmhzjhm=None, sfzhm=None, dysfzhm=None):
        """
        公共参数
        """
        super().__init__()
        self.url = "http://59.213.91.249/exchangegateway/"
        self.query["apiToken"] = apiToken
        if zjhm:
            self.query["zjhm"] = zjhm
        if sfzh:
            self.query["sfzh"] = sfzh
        if dmhzjhm:
            self.query["dmhzjhm"] = dmhzjhm
        if sfzhm:
            self.query["sfzhm"] = sfzhm
        if dysfzhm:
            self.query["dysfzhm"] = dysfzhm
        # TODO param

    @staticmethod
    def get_temporary_element_data(url):
        headers = {
            "qjyqmjg": "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",
            "djyqmyw": "pageNum=1&pageSize=10&appCode=2e6ffd2af686c28359a42d0e2b837022&apiToken=0145a29277774280b2d3beb6f9a17457&qqfyyId=test&qqfyymc=test&qqrid=test&qqr=test"
        }
        try:
            # 取消验证
            data = requests.get(url=url, headers=headers, verify=False).json()
        except Exception as e:
            print(f'临时接口获取失败{e}')
            return 0
        return data

    @staticmethod
    def get_A3_02_03_mianzhu(user_data: dict):
        # url=self.url+element_indexname_apiToken_path["绵竹市-根据姓名查询教师资格认证信息"]["path"]+self.query
        return 0

    @staticmethod
    def get_A3_02_03_shifang(user_data: dict):
        return 0

    @staticmethod
    def get_A3_02_03_jingyang(user_data: dict):
        """
        旌阳区-根据身份证查询教师资格认定合格人员信息
        """
        data = {
            'sfzhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["旌阳区-根据身份证查询教师资格认定合格人员信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["旌阳区-根据身份证查询教师资格认定合格人员信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('旌阳区-根据身份证查询教师资格认定合格人员信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_A3_02_03_guanghan(user_data: dict):
        """
        广汉市-教师资格认定人员名册
        """
        data = {
            'zjhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["广汉市-教师资格认定人员名册"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["广汉市-教师资格认定人员名册"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('广汉市-教师资格认定人员名册',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_A3_02_02(user_data: dict):
        """
        市文旅局-根据身份证查询德阳市导游资格信息
        """
        data = {
            'sfzh': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市文旅局-根据身份证查询德阳市导游资格信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市文旅局-根据身份证查询德阳市导游资格信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市文旅局-根据身份证查询德阳市导游资格信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_A3_02_01(user_data: dict):
        """
        市司法局-根据身份证查询律师执业信息
        """
        data = {
            'zjhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市司法局-根据身份证查询律师执业信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市司法局-根据身份证查询律师执业信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市司法局-根据身份证查询律师执业信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_C1_03_02(user_data: dict):
        """
        市自然资源局-根据身份证号查询个人抵押信息
        """
        data = {
            'dysfzhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市自然资源局-根据身份证号查询个人抵押信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市自然资源局-根据身份证号查询个人抵押信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市自然资源局-根据身份证号查询个人抵押信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_C1_03_01(user_data: dict):
        """
        市住建局-德阳市根据买方身份信息获取存量房合同
        """
        url = 'https://59.213.91.249/exchangegateway/szjj/gjmfsfxxhqclfht'

        data = {
            "ACTION": "GET_XJSPFYSHT_BY_SFZJ",
            "FDMC": user_data['sfzh'],
            "ZJHM": user_data['xm'],
            "qqfyyId": 'test',
            "qqfyymc": 'test',
            "qqrId": 'test',
            "qqr": 'test',
        }
        headers = {
            "appCode": TemporaryElements.get_appCode(),
            'apiToken': '115305536eb2486a88e1198b711aadcf',
            "qjyqmjg": "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",
            "djyqmyw": "pageNum=1&pageSize=10&appCode=2e6ffd2af686c28359a42d0e2b837022&apiToken=0145a29277774280b2d3beb6f9a17457&qqfyyId=test&qqfyymc=test&qqrid=test&qqr=test"

        }
        try:
            # 取消验证
            result = requests.post(url=url, json=data, headers=headers, verify=False).json()
            print('市住建局-德阳市根据买方身份信息获取存量房合同',end='    ')
            print(result)
            if result['code'] == 200:
                if isinstance(result['data'], dict):
                    amount = len(result['data'])
                    if amount > 1:
                        amount = 2
                    return amount
                else:
                    return 0
        except Exception as e:
            print(f'临时接口获取失败{e}')
            return 0

    @staticmethod
    def get_D2_01_01(user_data: dict):
        """
        市发改委-失信被执行人名单信息
        """
        data = {
            'dmhzjhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市发改委-失信被执行人名单信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市发改委-失信被执行人名单信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市发改委-失信被执行人名单信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_D1_01_01(user_data: dict):
        """
        市发改委-根据自然人身份证号码查询行政处罚信息
        """
        data = {
            'sfzhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市发改委-根据自然人身份证号码查询行政处罚信息"]["apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市发改委-根据自然人身份证号码查询行政处罚信息"][
            "path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市发改委-根据自然人身份证号码查询行政处罚信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    @staticmethod
    def get_E2_02(user_data: dict):
        """
        市自然资源局-根据身份证号码查询德阳市自然人表彰信息
        """
        data = {
            'zjhm': user_data['sfzh'],
            'apiToken': element_indexname_apiToken_path["市自然资源局-根据身份证号码查询德阳市自然人表彰信息"][
                "apiToken"]
        }
        temporary_element = TemporaryElement(**data)
        url = temporary_element.url + element_indexname_apiToken_path["市自然资源局-根据身份证号码查询德阳市自然人表彰信息"]["path"] + parse.urlencode(
            temporary_element.query)
        result = temporary_element.get_temporary_element_data(url)
        if result:
            print('市自然资源局-根据身份证号码查询德阳市自然人表彰信息',end='    ')
            print(result)
            return 1 if result["data"] else 0

    # def get_E2_02_03(self):
    #     pass
    #
    # def get_E2_02_02(self):
    #     pass
    #
    # def get_E2_02_01(self):
    #     pass


class UserIndex:
    @staticmethod
    def get_A1_02_01(user_data: dict):
        """
        婚姻状况
        """
        pass
        return 0

    @staticmethod
    def get_A2_01_01(user_data: dict):
        """
        近5年是否缴纳社保
        """
        pass
        return 0

    @staticmethod
    def get_A2_01_02(user_data: dict):
        """
        近五年社保累计缴纳时间
        """
        return Element.get_social_security_payment_months(user_data)

    @staticmethod
    def get_A3_01_01(user_data: dict):
        """
        工作类型
        """
        # TODO 无数据来源
        return 'None'

    @staticmethod
    def get_A3_02_01(user_data: dict):
        """
        是否具有律师执业资格
        """
        return TemporaryElement.get_A3_02_01(user_data)

    @staticmethod
    def get_A3_02_02(user_data: dict):
        """
        是否具有导游资格
        """
        return TemporaryElement.get_A3_02_02(user_data)

    @staticmethod
    def get_A3_02_03(user_data: dict):
        """
        教师资格
        """
        result = TemporaryElement.get_A3_02_03_mianzhu(user_data)
        if result:
            return result
        result = TemporaryElement.get_A3_02_03_shifang(user_data)
        if result:
            return result
        result = TemporaryElement.get_A3_02_03_jingyang(user_data)
        if result:
            return result
        result = TemporaryElement.get_A3_02_03_guanghan(user_data)
        if result:
            return result
        return 0

    @staticmethod
    def get_A3_02_04(user_data: dict):
        """
        是否具有其他职业资格
        """
        # TODO 无数据来源
        return 'None'

    @staticmethod
    def get_C1_03_01(user_data: dict):
        """
        个人房产数量
        """
        # TODO POST
        return TemporaryElement.get_C1_03_01(user_data)

    @staticmethod
    def get_C1_03_02(user_data: dict):
        """
        个人被抵押房产数量
        """
        return TemporaryElement.get_C1_03_02(user_data)

    @staticmethod
    def get_C2_01_01(user_data: dict):
        """
        账户状态
        """
        pass
        return 0

    @staticmethod
    def get_C2_01_02(user_data: dict):
        """
        账户余额
        """
        pass
        return 0

    @staticmethod
    def get_C2_01_03(user_data: dict):
        """
        缴存基数
        """
        pass
        return 0

    @staticmethod
    def get_C2_02_01(user_data: dict):
        """
        贷款业务明细类型
        """
        pass
        return 0

    @staticmethod
    def get_C2_02_02(user_data: dict):
        """
        罚息金额
        """
        pass
        return 0

    @staticmethod
    def get_D1_01_01(user_data: dict):
        """
        近5年被行政处罚的次数
        """
        return TemporaryElement.get_D1_01_01(user_data)

    @staticmethod
    def get_D2_01_01(user_data: dict):
        """
        近5年被列入失信被执行人的次数
        """
        return TemporaryElement.get_D2_01_01(user_data)

    @staticmethod
    def get_D2_03_01(user_data: dict):
        """
        近5年税务违约的次数
        """
        pass
        return 0

    @staticmethod
    def get_D3_01_01(user_data: dict):
        """
        近5年发生失信行为的次数（包括被列入失信黑名单、列入经营异常、失信被执行等）
        """
        pass
        return 0

    @staticmethod
    def get_E2_02_01(user_data: dict):
        """
        近5年获得县（区）级荣誉的次数
        """
        return TemporaryElement.get_E2_02(user_data)

    @staticmethod
    def get_E2_02_02(user_data: dict):
        """
        近5年获得市级荣誉的次数
        """
        return TemporaryElement.get_E2_02(user_data)

    @staticmethod
    def get_E2_02_03(user_data: dict):
        """
        近5年获得省级荣誉的次数
        """
        return TemporaryElement.get_E2_02(user_data)

    @staticmethod
    def get_E2_02_04(user_data: dict):
        """
        近5年获得国家级荣誉的次数
        """
        return TemporaryElement.get_E2_02(user_data)

    @staticmethod
    def get_user_indexs(user_data: dict):
        user_indexs = {
            "A1_02_01": UserIndex.get_A1_02_01(user_data),
            "A2_01_01": UserIndex.get_A2_01_01(user_data),
            "A2_01_02": UserIndex.get_A2_01_02(user_data),
            "A3_01_01": UserIndex.get_A3_01_01(user_data),
            "A3_02_01": UserIndex.get_A3_02_01(user_data),
            "A3_02_02": UserIndex.get_A3_02_02(user_data),
            "A3_02_03": UserIndex.get_A3_02_03(user_data),
            "A3_02_04": UserIndex.get_A3_02_04(user_data),
            "C1_03_01": UserIndex.get_C1_03_01(user_data),
            "C1_03_02": UserIndex.get_C1_03_02(user_data),
            "C2_01_01": UserIndex.get_C2_01_01(user_data),
            "C2_01_02": UserIndex.get_C2_01_02(user_data),
            "C2_01_03": UserIndex.get_C2_01_03(user_data),
            "C2_02_01": UserIndex.get_C2_02_01(user_data),
            "C2_02_02": UserIndex.get_C2_02_02(user_data),
            "D1_01_01": UserIndex.get_D1_01_01(user_data),
            "D2_01_01": UserIndex.get_D2_01_01(user_data),
            "D2_03_01": UserIndex.get_D2_03_01(user_data),
            "D3_01_01": UserIndex.get_D3_01_01(user_data),
            "E2_02_01": UserIndex.get_E2_02_01(user_data),
            "E2_02_02": UserIndex.get_E2_02_02(user_data),
            "E2_02_03": UserIndex.get_E2_02_03(user_data),
            "E2_02_04": UserIndex.get_E2_02_04(user_data),
        }

        return user_indexs


user_list = [
    {'sfzh': '510623198009210017', 'xm': '刘辉'},
    {'sfzh': '510603198511186678', 'xm': '唐龑'},
    {'sfzh': '510622199608195718', 'xm': '何颖'},
    {'sfzh': '510625199507110016', 'xm': '郭朋鑫'},
    {'sfzh': '510723199804070017', 'xm': '胡笛潇'},
    {'sfzh': '510603199303110303', 'xm': '杨春桃'},
    {'sfzh': '510603199702240985', 'xm': '邓雨桐'},
    {'sfzh': '500229199510210220', 'xm': '周付琴'},
    {'sfzh': '510682198512240029', 'xm': '曾潇潇'},
    {'sfzh': '510723199705030044', 'xm': '贾丽莎'},
    {'sfzh': '510603198701115969', 'xm': '李仁可'},
    {'sfzh': '510682198707070031', 'xm': '赖韬'},
    {'sfzh': '510682198607010525', 'xm': '边明思'},
    {'sfzh': '510602199606227661', 'xm': '朱航'},
    {'sfzh': '510602197601261693', 'xm': '曾振金'},
    {'sfzh': '511025197309216791', 'xm': '周龙生'},
    {'sfzh': '513721199009081008', 'xm': '张又杉'},
    {'sfzh': '51060319931108783X', 'xm': '邓杰堃'},
    {'sfzh': '510603199705095939', 'xm': '邱奕铭'},
    {'sfzh': '510622199510103010', 'xm': '董永亮'},
    {'sfzh': '510623199606040815', 'xm': '龚荣志'},
    {'sfzh': '510722199401270026', 'xm': '曾小苡'},
    {'sfzh': '510622199508123012', 'xm': '牟小虎'},
    {'sfzh': '51068320000831091X', 'xm': '杜沛霖'},
    {'sfzh': '510603198710262047', 'xm': '罗琛'},
    {'sfzh': '510623199606292115', 'xm': '满光东'},
    {'sfzh': '510681199908230319', 'xm': '廖朗迅'},
    {'sfzh': '510683200105220027', 'xm': '梅筱璐'},
    {'sfzh': '141034199606110068', 'xm': '王舒婷'},
    {'sfzh': '510603198602056502', 'xm': '肖燕燕'},
]


def get_user_scores(user_data: dict):
    user_indexs = UserIndex.get_user_indexs(user_data)
    print('user_indexs')
    print(user_indexs)
    user_scores = calculate_user_scores(user_indexs)
    return user_scores


for i in user_list:
    print(i)
    print(get_user_scores(i))
    print('---------------------------------------------------------------------')
