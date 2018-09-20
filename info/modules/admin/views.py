import calendar
from datetime import datetime, timedelta, date
from .auth import generate_token, verify_token
from flask import jsonify, request, session, render_template
from info import db
from info import redis_store
from info.models import User, AgentInfo, Stat, AdOrder
from info.utils.response_code import RET
from . import admin_blue
from info.utils.image_storage import storage


@admin_blue.route('/RAM/register', methods=['POST'])
def register():
    '''后台注册'''
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    position = request.get_json().get('position')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='用户已存在')
    new_user = User()
    new_user.username = username
    new_user.set_password(password)
    if position:
        new_user.position = position
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(errno=RET.SERVERERR, errmsg='注册失败')
    return jsonify(errno=RET.OK, errmsg='注册成功')


@admin_blue.route('/login', methods=['POST'])
def login():
    '''后台统计登录'''
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if not user.check_password(password):
            return jsonify(errno=RET.LOGINERR, errmsg='密码错误')
        session['username'] = username
        session["user_id"] = user.id
        # 登录验证成功后生成一个token存在redis中，设置了有效期2h，并返回
        token = generate_token(username=username).decode('ascii')
        data = []
        res = {
            'user_id': user.id,
            'username': user.username,
            'token': token
        }
        data.append(res)
        return jsonify(errno=RET.OK, data=data, errmsg='登录成功')
    except Exception as e:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')


@admin_blue.route('/logout')
def logout():
    '''注销'''
    session.pop('username')
    session.pop('user_id')
    return jsonify(errno=RET.OK, errmsg='登出成功')


@admin_blue.route('/retrievePassword', methods=['POST'])
def retrieve_password():
    '''忘记密码并重置密码'''
    username = request.get_json().get('username')
    new_password = request.get_json().get('new_password')
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = new_password
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
        else:
            return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    except:
        return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')
    return jsonify(errno=RET.OK, errmsg='修改成功')

@admin_blue.route('/showUser',methods=['POST'])
def show_user():
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if not user.check_password(password):
            return jsonify(errno=RET.LOGINERR, errmsg='密码错误')
        if user.position == '5':
            users = User.query.all()
            user_info = [User.to_dict(user) for user in users]
            return jsonify(errno=RET.OK,user_info=user_info,  errmsg='查找成功')
        return jsonify(errno=RET.USERERR,errmsg='权限不够')
    except Exception as e:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

@admin_blue.route('/agentReview', methods=['GET', 'POST'])
@admin_blue.route('/agentReview/<int:page>', methods=['GET', 'POST'])
def agent_review(page=1):
    '''代理申请审核'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')
    if request.method == 'POST':
        # 提交审核请求 0表示待审核 1表示审核通过 2 审核驳回
        status = request.get_json().get('status')
        agent_id = request.get_json().get('agent_id')
        try:
            agents = AgentInfo.query.filter(AgentInfo.id == agent_id).filter(AgentInfo.is_delete == 0)
            for agent in agents:
                agent.status = status
                db.session.add(agent)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
                return jsonify(errno=RET.OK, errmsg='提交成功')
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    else:
        # 显示待审核列表
        current_page = request.args.get('current_page', page)
        per_page = request.args.get('per_page', 5)
        # 查询封装返回
        agent_info = []
        filter = [AgentInfo.status == 0, AgentInfo.is_delete == 0]
        try:
            pag = AgentInfo.query.filter(*filter).order_by(AgentInfo.create_time.desc()).paginate(current_page,
                                                                                                  per_page,
                                                                                                  error_out=False)
            agents = pag.items
            total_page = pag.pages
            page = pag.page
            for agent in agents:
                climg_db_url = agent.collection_QR_code
                climg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + climg_db_url
                wcimg_db_url = agent.wechat_QR_code
                wcimg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + wcimg_db_url
                agt = {
                    'agent_id': agent.id,
                    'name': agent.name,
                    'phone_number': agent.phone_number,
                    'original_wechat': agent.original_wechat,
                    'current_fans': agent.current_fans,
                    'province': agent.province,
                    'city': agent.city,
                    'county': agent.county,
                    'wechat_QR_code': wcimg_url,
                    'collection_QR_code': climg_url,
                    'create_time': agent.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': agent.status,
                }
                agent_info.append(agt)
            count = AgentInfo.query.filter_by(status=0, is_delete=0).count()
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
        return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok', page=page, total_page=total_page, count=count)


@admin_blue.route('/agentList/<int:page>', methods=['GET', 'POST'])
@admin_blue.route('/agentList', methods=['GET', 'POST'])
def agent_list(page=1):
    '''已审核代理列表'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')

    if request.method == 'POST':
        # POST请求删除申请表和统计表
        agent_id = request.get_json().get('agent_id')
        try:
            agents = AgentInfo.query.filter_by(id=agent_id, is_delete=0, status=1)
            for agent in agents:
                agent.is_delete = 1
                db.session.add(agent)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
            return jsonify(errno=RET.OK, errmsg='提交成功')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='删除失败，请重试')
    else:
        # GET请求显示已审核列表
        current_page = request.args.get('current_page', page)
        per_page = request.args.get('per_page', 5)
        agent_info = []
        filter = [AgentInfo.status == 1, AgentInfo.is_delete == 0]
        try:
            pag = AgentInfo.query.filter(*filter).order_by(AgentInfo.create_time.desc()).paginate(current_page,
                                                                                                  per_page,
                                                                                                  error_out=False)
            agents = pag.items
            total_page = pag.pages
            page = pag.page
            for agent in agents:
                # 拼接七牛云图片链接
                climg_db_url = agent.collection_QR_code
                climg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + climg_db_url
                wcimg_db_url = agent.wechat_QR_code
                wcimg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + wcimg_db_url
                if agent.current_fans == None:
                    agent.current_fans = agent.original_fans
                agt = {
                    'id': agent.id,
                    'name': agent.name,
                    'phone_number': agent.phone_number,
                    'original_wechat': agent.original_wechat,
                    'original_fans': agent.original_fans,
                    'current_fans': agent.current_fans,
                    'province': agent.province,
                    'city': agent.city,
                    'county': agent.county,
                    'wechat_QR_code': wcimg_url,
                    'collection_QR_code': climg_url,
                    'create_time': agent.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': agent.status,
                }
                agent_info.append(agt)
            count = AgentInfo.query.filter_by(status=1, is_delete=0).count()
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
        return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok', total_page=total_page, page=page, count=count)


@admin_blue.route('/registration', methods=['GET', 'POST'])
def registration():
    '''代理日常加粉统计'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')

    if request.method == 'POST':
        agent_id = request.get_json().get('agent_id')
        today_fans = request.get_json().get('today_fans')
        if not redis_store.get('agent_current_fans_' + str(agent_id)):
            # 判断redis中是否存有今日当前的粉丝量
            agents = AgentInfo.query.filter_by(id=agent_id, is_delete=0)
            for agent in agents:
                today = datetime.now()
                expire_time = datetime(today.year, today.month, today.day, 23, 59, 59)  # 有效期至当天的23：59：59
                stat = Stat()
                stat.agent_id = agent_id
                stat.today_fans = int(today_fans)
                redis_store.set('agent_current_fans_' + str(agent_id), agent.current_fans)
                redis_store.expireat('agent_current_fans_' + str(agent_id), expire_time)
                agent.current_fans = agent.current_fans + int(today_fans)
                stat.total_fans = agent.current_fans
                db.session.add(agent)
                db.session.add(stat)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
            agent_info = [AgentInfo.to_dict(agent) for agent in agents]
            return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok')
        else:
            # 如果redis存在今日当前的粉丝量，则不允许提交
            return jsonify(errno=RET.DATAERR, errmsg='你已提交')
    else:
        try:
            agents = AgentInfo.query.filter(AgentInfo.status == 1).filter(AgentInfo.is_delete == 0)
            agent_info = [AgentInfo.to_dict(agent) for agent in agents]
            return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询错误')


@admin_blue.route('/modification', methods=['POST'])
def modification():
    '''代理日常加粉修改'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')

    if request.method == 'POST':
        agent_id = request.get_json().get('agent_id')
        today_fans = request.get_json().get('today_fans')
        if not redis_store.get('agent_current_fans_' + str(agent_id)):
            return jsonify(errno=RET.NODATA, errmsg='请先添加数据')
        try:
            agents = AgentInfo.query.filter_by(id=agent_id, is_delete=0)
            stats = Stat.query.filter_by(agent_id=agent_id)
            for agent in agents:
                agent.current_fans = int(redis_store.get('agent_current_fans_' + str(agent_id))) + int(today_fans)
                db.session.add(agent)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return jsonify(errno=RET.SERVERERR, errmsg='提交失败')

                for stat in stats:
                    if stat.create_time.date() == date.today():
                        stat.today_fans = today_fans
                        stat.total_fans = agent.current_fans
                        db.session.add(stat)
                        try:
                            db.session.commit()
                            return jsonify(errno=RET.OK, errmsg='提交成功')
                        except Exception as e:
                            db.session.rollback()
                            return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
            agent_info = [AgentInfo.to_dict(agent) for agent in agents]
            return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询失败')


@admin_blue.route('/weekFans', methods=['POST'])
def week_fans():
    '''代理七天统计'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')

    if request.method == 'POST':
        agent_id = request.get_json().get('agent_id')
        today = datetime.today()
        seven_days_ago = today + timedelta(days=-7)
        try:
            stats = Stat.query.filter(Stat.create_time.between(seven_days_ago, today)).filter(
                Stat.agent_id == agent_id)
            stat_info = [Stat.to_dict(stat) for stat in stats]
            return jsonify(errno=RET.OK, stat_info=stat_info, errmsg='ok')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询失败')


def getdate(year=None, month=None):
    '''获取当月的第一天和总天数'''
    if year:
        year = int(year)
    else:
        year = datetime.today().year
    if month:
        month = int(month)
    else:
        month = datetime.today().month
    # 获取当月第一天的星期和当月的总天数
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)
    # 获取当月的第一天
    firstDay = datetime(year=year, month=month, day=1)
    lastDay = datetime(year=year, month=month, day=monthRange)

    return firstDay, lastDay


@admin_blue.route('/monthFans', methods=['POST'])
def month_fans():
    '''代理月份统计'''
    # 校验token
    token = request.headers.get('Authorization')
    data = verify_token(token)
    if data == False:
        return jsonify(errno=RET.DATAERR, errmsg='校验token失败')

    if request.method == 'POST':
        year = request.get_json().get('year')
        month = request.get_json().get('month')
        agent_id = request.get_json().get('agent_id')
        firstDay, lastDay = getdate(year=year, month=month)
        try:
            stats = Stat.query.filter(Stat.create_time.between(firstDay, lastDay)).filter(
                Stat.agent_id == agent_id)
            stat_info = [Stat.to_dict(stat) for stat in stats]
            return jsonify(errno=RET.OK, stat_info=stat_info, errmsg='ok')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询失败')


@admin_blue.route('/AdOrder', methods=['GET', 'POST'])
def adorder(page=1):
    '''广告接单登记'''
    if request.method == 'POST':
        # 填写广告接单记录
        agent_id = request.get_json().get('agent_id')
        date_of_order = request.get_json().get('date_of_order')
        push_time = request.get_json().get('push_time')
        ad_count = request.get_json().get('ad_count')
        screenshots = request.files.get('screenshots')
        amount = request.get_json().get('amount')
        check_out_date = request.get_json().get('check_out_date')
        state = request.get_json().get('state')
        remark = request.get_json().get('remark')
        try:
            screenshots = storage(screenshots.read())
        except:
            return jsonify(errno=RET.THIRDERR, errmsg='上传图片错误')

        new_adorder = AdOrder()
        new_adorder.agent_id = agent_id
        new_adorder.date_of_order = date_of_order
        new_adorder.push_time = push_time
        new_adorder.ad_count = ad_count
        new_adorder.screenshots = screenshots
        new_adorder.amount = amount
        new_adorder.check_out_date = check_out_date
        new_adorder.state = state
        new_adorder.remark = remark
        db.session.add(new_adorder)
        try:
            db.session.comnit()
        except:
            db.session.rollback()
            return jsonify(errno=RET.SERVERERR, errmsg='提交失败')
        return jsonify(errno=RET.OK, errmsg='提交成功')
    else:
        # GET请求显示广告登记表明细
        current_page = request.args.get('current_page', page)
        per_page = request.args.get('per_page', 5)
        agent_info = []
        filter = [AgentInfo.status == 1, AgentInfo.is_delete == 0]
        try:
            pag = AgentInfo.query.filter(*filter).order_by(AgentInfo.create_time.desc()).paginate(current_page,
                                                                                                  per_page,
                                                                                                  error_out=False)
            agents = pag.items
            total_page = pag.pages
            page = pag.page
            for agent in agents:
                # 拼接七牛云图片链接
                climg_db_url = agent.collection_QR_code
                climg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + climg_db_url
                wcimg_db_url = agent.wechat_QR_code
                wcimg_url = 'http://pe9wqjxpq.bkt.clouddn.com/' + wcimg_db_url
                adorders = AdOrder.query.filter_by(agent_id=agent.id)
                for adorder in adorders:
                    agt = {
                        'id': agent.id,
                        'name': agent.name,
                        'phone_number': agent.phone_number,
                        'original_wechat': agent.original_wechat,
                        'current_fans': agent.current_fans,
                        'province': agent.province,
                        'city': agent.city,
                        'county': agent.county,
                        'wechat_QR_code': wcimg_url,
                        'collection_QR_code': climg_url,
                        'date_of_order': adorder.date_of_order,
                        'push_time': adorder.push_time,
                        'ad_count': adorder.ad_count,
                        'screenshots': adorder.screenshots,
                        'amount': adorder.amount,
                        'check_out_date': adorder.check_out_date,
                        'state': adorder.state,
                        'remark': adorder.remark
                    }
                    agent_info.append(agt)
            count = AgentInfo.query.filter_by(status=1, is_delete=0).count()
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
        return jsonify(errno=RET.OK, agent_info=agent_info, errmsg='ok', total_page=total_page, page=page, count=count)


@admin_blue.route('/chargeList', methods=['POST'])
def chargeList():
    '''费用清单'''
    if request.method == 'POST':
        year = request.get_json().get('year')
        month = request.get_json().get('month')
        agent_id = request.get_json().get('agent_id')
        firstDay, lastDay = getdate(year=year, month=month)
        try:
            adorders = AdOrder.query.filter(Stat.create_time.between(firstDay, lastDay)).filter(
                AdOrder.agent_id == agent_id)
            adorder_info = [AdOrder.to_dict(adorder) for adorder in adorders]
            return jsonify(errno=RET.OK, stat_info=adorder_info, errmsg='ok')
        except Exception as e:
            return jsonify(errno=RET.SERVERERR, errmsg='数据库查询失败')


@admin_blue.route('/')
def index():
    return render_template('company_admin/index.html')
