# coding=utf-8
import random
import re

from flask import current_app
from flask import request, jsonify

from info import redis_store, db
from info.models import User, AgentInfo
from info.utils.image_storage import storage
from . import passport_blu
from flask import make_response
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info import constants
from flask import session


@passport_blu.route('/checkUser', methods=['POST'])
def check_user():
    '''检测用户手机号，用户名或微信号是否已经被注册'''
    username = request.get_json().get('username')
    mobile = request.get_json().get('mobile')
    original_wechat = request.get_json().get('original_wechat')
    if username:
        try:
            user = User.query.filter_by(username=username).first()
            if user != None:
                return jsonify(errno=RET.DATAEXIST, errmsg='用户已存在')
        except:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')
    elif mobile:
        try:
            agent = AgentInfo.query.filter_by(phone_number=mobile).first()
            if agent != None:
                return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已被注册')
            user = User.query.filter_by(phone_number=mobile).first()
            if user != None:
                return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已被注册')
        except:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')
    else:
        try:
            agent = AgentInfo.query.filter_by(original_wechat=original_wechat,is_delete=0).first()
            if agent != None:
                return jsonify(errno=RET.DATAEXIST, errmsg='该微信号已注册')
        except:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')
    return jsonify(errno=RET.OK, errmsg='该手机号未注册过，可正常注册')


@passport_blu.route('/retrievePassword', methods=['POST'])
def retrieve_password():
    '''忘记密码并重置密码'''
    mobile = request.get_json().get('mobile')
    sms_code = request.get_json().get('sms_code')
    new_password = request.get_json().get('new_password')
    # 调取redis查询手机验证码
    try:
        rel_sms_code = redis_store.get('smscode:%s' % mobile)
    except Exception as e:
        print(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询出错')

    if not rel_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if rel_sms_code == sms_code:
        return jsonify(errno=RET.OK, errmsg='短信验证码校验成功')
    try:
        user = User.query.filter_by(phone_number=mobile).first()
        if user:
            user.password = new_password
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
        else:
            return jsonify(errno=RET.USERERR,errmsg='用户不存在')
    except:
        return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')
    return jsonify(errno=RET.OK, errmsg='修改成功')


@passport_blu.route('/proxy/register', methods=['POST'])
def proxy_register():
    '''代理申请信息'''
    user_name = request.form.get('user_name')
    cmbProvince = request.form.get('cmbProvince')
    cmbCity = request.form.get('cmbCity')
    cmbArea = request.form.get('cmbArea')
    wechatID = request.form.get('wechatID')
    phone = request.form.get('phone')
    fanNumber = request.form.get('fanNumber')
    phoneNum = request.form.get('phoneNum')

    if not all([user_name, cmbProvince, cmbArea, cmbCity, wechatID,
                phone, fanNumber, phoneNum]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    exampleInputFile = request.files.get('exampleInputFile')
    payFile = request.files.get('payFile')

    if not all([exampleInputFile, payFile]):
        return jsonify(errno=RET.PARAMERR, errmsg='文件缺失')

    try:
        key1 = storage(exampleInputFile.read())
        key2 = storage(payFile.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片文件包错误')

    agent = AgentInfo()
    agent.wechat_QR_code = key1
    agent.collection_QR_code = key2
    agent.name = user_name
    agent.province = cmbProvince
    agent.city = cmbCity
    agent.county = cmbArea
    agent.original_wechat = wechatID
    agent.phone_number = phone
    agent.original_fans = fanNumber
    agent.current_fans = agent.original_fans
    agent.num_mobile = phoneNum

    try:
        db.session.add(agent)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库操作失败')
    return jsonify(errno=RET.OK, errmsg='提交成功')


@passport_blu.route('/login', methods=['POST'])
def login():
    '''登录'''
    # username = request.get_json().get('username')
    # phone_number = request.get_json().get('phone')
    # password = request.get_json().get('password')
    req_dict = request.json
    if not req_dict :
        return jsonify(errno = RET.PARAMERR,errmsg = '缺少参数请校验您输入参数')

    re = req_dict['re']
    username = req_dict['username']
    password = req_dict['password']

    if not all([re,username,password]):
        return jsonify(errno = RET.PARAMERR,errmsg='缺少校验参数请检查')
    try:
        re = int(re)
    except Exception as e :
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误请检查')
        current_app.logger.error(e)

    # 查询用户身份
    if re == 2:
        try:
            user = User.query.filter(User.username == username).first()
            # 比对密码
            if not user.check_password(password):
                return jsonify(errno=RET.ROLEERR, errmsg='身份验证失败密码错误')
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='查询数据库错误')
            current_app.logger.error(e)

    elif re == 1:
        try:
            user = User.query.filter_by(phone_number=username).first()
            # 比对密码
            if not user.check_password(password):
                return jsonify(errno=RET.ROLEERR, errmsg='身份验证失败密码错误')
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='查询数据库错误')

    # 记住用户登陆状态
    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify(errno=RET.OK,
                   errmsg='登陆成功',
                   username=user.username)


@passport_blu.route('/register', methods=['POST', 'GET'])
def register():
    '''注册'''
    webJson = request.json

    if not webJson:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    username = webJson['username']
    mobile = webJson['mobile']
    sms_code = webJson['sms_code']
    password = webJson['password']

    if not all([mobile, sms_code, password, username]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 调取redis查询手机验证码
    try:
        rel_sms_code = redis_store.get('smscode:%s' % mobile)
    except Exception as e:
        print(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询出错')

    if not rel_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    user = User()
    user.username = username
    user.phone_number = mobile
    user.set_password(password)  # 密码加密存储
    user.position = 3

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库写入错误')

    return jsonify(errno=RET.OK, errmsg='注册成功')


@passport_blu.route('/logout')
def logout():
    '''注销'''
    session.pop('username')
    session.pop('user_id')
    return jsonify(errno=RET.OK, errmsg='登出成功')


# 手机短信验证路由
@passport_blu.route('/mobile_code', methods=['POST'])
def send_sms_code():
    # 获取前台返回json数据三个参数（手机号，图片验证码，图片验证码id）
    req_dict = request.json
    if not req_dict:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    print(req_dict.get('phone_number'))
    mobile = req_dict['phone_number']
    if not mobile:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    user = User.query.filter_by(phone_number=mobile).first()
    if user:
        return jsonify(errno=RET.DATAEXIST,errmsg='该手机号已经被注册')
    sms_code = '%06d' % random.randint(0, 999999)
    print('短信验证码为:' + sms_code)
    # 将生成的验证码存入redis中
    try:
        redis_store.set('smscode:%s' % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        print(e)
        return jsonify(errno=RET.DBERR, errmsg='redis数据库存储错误')
    # 发送短信给用户(云通讯)
    from .cloopen import message_validate
    result, err_message = message_validate(mobile, sms_code)
    if not result:
        return jsonify(errno=RET.SERVERERR,errmsg=err_message)




    # from info.lib.yuntongxun.sms import CCP
    # try:
    #     ccp = CCP()
    #     res = ccp.send_template_sms(mobile, [str(sms_code), constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    # except Exception as e:
    #     print(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')
    # if res != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')

    print('发送成功')
    return jsonify(errno=RET.OK, errmsg='短信发送成功')


@passport_blu.route('/advance', methods=['POST'])
def advance():
    '''申请进度查询'''
    phone_number = request.get_json().get('phone')
    try:
        agent = AgentInfo.query.filter_by(phone_number=phone_number).first()
    except:
        return jsonify(errno=RET.SERVERERR, errmsg='数据库查询失败')
    if agent == None:
        return jsonify(errno=RET.NODATA, errmsg='数据不存在')
    agent_status = int(agent.status)
    if agent_status == 0:
        return jsonify(errno=RET.OK, agent_status=agent_status, errmsg='待审核')
    if agent_status == 1:
        return jsonify(errno=RET.OK, agent_status=agent_status, errmsg='审核通过')
    if agent_status == 2:
        return jsonify(errno=RET.OK, agent_status=agent_status, errmsg='审核未通过')
