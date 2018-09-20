# coding:utf-8
import datetime
import hashlib
import requests
import json
import base64


def message_validate(phone_number, validate_number):
    # 说明：主账号，登陆云通讯网站后，可在控制台首页中看到开发者主账号ACCOUNT SID。
    accountSid = "xxxxxxxxx"
    # 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN。
    accountToken = "xxxxxxxxx"
    # 请使用管理控制台中已创建应用的APPID。
    appid = "xxxxxxxxxxxx"
    # templateId = '1'
    templateId = '336164'  # 上线修改模板id
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    signature = accountSid + accountToken + now
    m = hashlib.md5()
    m.update(signature.encode('utf-8'))
    sigParameter = m.hexdigest().upper()
    # 说明：REST API版本号保持不变。
    url = "https://app.cloopen.com:8883/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s" % (
        accountSid, sigParameter)
    # 请求地址
    authorization = accountSid + ':' + now  # 授权码
    authorization = bytes(authorization, encoding='utf-8')
    new_authorization = base64.b64encode(authorization).strip()

    headers = {'content-type': 'application/json;charset=utf-8', 'accept': 'application/json',
               'Authorization': new_authorization}
    data = {'to': phone_number, 'appId': appid, 'templateId': templateId, 'datas': [str(validate_number), '3']}
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    if response.json()['statusCode'] == '000000':
        return True, response.json().get('statusMsg')
    else:
        return False, response.json().get('statusMsg')


if __name__ == '__main__':
    result, reason = message_validate('xxxxxxxxxxxx', '123456')
    if result:
        print('发送成功')
    else:
        print('发送失败')
        print('原因是:' + reason)
