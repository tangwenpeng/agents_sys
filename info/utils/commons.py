# coding=utf8


# 定义新闻点击样式类过滤器
from flask import abort
from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import session
import functools

from info import constants
from info.models import User
from info.utils.response_code import RET

def do_status_change(status):
    assert status in [0, 1, -1], 'status取值必须在0,1,-1中'
    status_dict = {
        0: '审核通过',
        1: '审核中',
        -1: '审核不通过'
    }
    return status_dict[status]


def do_rank_class(index):
    if index < 0 or index >= 3:
        return ''
    rank_class_li = ['first', 'second', 'third']
    return rank_class_li[index]


def login_user_data(view_func):
    @functools.wraps(view_func)
    def wrapper(*args,**kwargs):
        user = None
        user_id = session.get('user_id')
        if user_id:
            try:
                user = User.query.get(user_id)
                user.avatar_url_path = constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else ''
            except Exception as e:
                print(e)
        g.user = user
        return view_func(*args, **kwargs)
    return wrapper


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg='该用户尚未登陆')

        if user_id:
            try:
                user = User.query.get(user_id)
                user.avatar_url_path = constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else ''
            except Exception as e:
                return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')

        g.user = user

        return view_func(*args, **kwargs)
    return wrapper


def admin_login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 尝试从session中获取user_id
        user_id = session.get('user_id')
        is_admin = session.get('is_admin')

        if not user_id or not is_admin:
            # 登录用户不是管理员或用户未登录，直接跳转到首页
            return redirect('/')

        user = None
        try:
            user = User.query.get(user_id)
            user.avatar_url_path = constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else ''
        except Exception as e:
            current_app.logger.error(e)
            abort(500)

        # 使用g变量临时保存user
        g.user = user

        return view_func(*args, **kwargs)
    return wrapper