import requests

url='http://172.19.0.2:8889/v1/score/mission'
data={
    "mission":"0"
}

headers = {'Content-Type': 'application/json;charset=UTF-8'}
result=requests.post(url=url,json=data,headers=headers).json()

print(result)