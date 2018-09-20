# coding=utf-8
from flask import current_app, jsonify
from flask import render_template
from flask import request

from info import constants
from info.utils.commons import login_user_data
from info.utils.response_code import RET
from . import index_blue


@index_blue.route('/', methods=['GET', 'POST'])
@login_user_data
def index():
    # user_id = session.get('user_id')
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #         # user.avatar_url= constants.QINIU_DOMIN_PREFIX+user.avatar_url
    #     except Exception as e:
    #         print(e)
    #user = g.user
    # 新闻分类
    return render_template('company_index/index.html')

# 返回静态网页图标
# @index_blue.route('/favicon.ico')
# def get_web_favicon():
#     return current_app.send_static_file('news/favicon.ico')
