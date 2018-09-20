from flask import abort
from flask import g, jsonify
from flask import render_template
from flask import request, current_app,session

from info import constants
from info import db
from info.models import User
from info.utils.image_storage import storage
from info.utils.commons import login_required
from info.utils.response_code import RET
from . import profile_blu


@profile_blu.route('/<int:user_id>/news')
@login_required
def user_other_news(user_id):
    page = request.args.get('p', 1)
    if not page:
        return jsonify(errno=RET.PARAMERR,errmsg='缺少参数')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数转换错误')

    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')

    if not author:
        return jsonify(errno=RET.PARAMERR,errmsg='没有该作者信息')

    # 分页查询新闻
    try:
        pagenation = author.news_list.paginate(page,constants.OTHER_NEWS_PAGE_MAX_COUNT,False)
        news_li = pagenation.items
        total_page = pagenation.pages
        current_page = pagenation.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='分页数据错误')
    news_dict_li=[]
    for news in news_li:
        news_dict_li.append(news.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='OK',
                   news_li=news_dict_li,
                   total_page=total_page,
                   current_page=current_page)

@profile_blu.route('/<int:user_id>')
@login_required
def user_other_detail(user_id):
    user = g.user
    try:
        author = User.query.get(user_id)
        author.avatar_url_path =constants.QINIU_DOMIN_PREFIX + author.avatar_url
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')

    is_follow = False
    if user in author.followers:
        is_follow = True

    return render_template('news/other.html', author=author, is_follow=is_follow)


@profile_blu.route('/follows')
@login_required
def user_follows():
    """
    用户关注的其他用户:
    """
    # 1. 接收参数并进行参数校验
    page = request.args.get('p', 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 2. 获取用户收藏的新闻信息并进行分页
    # 获取登录用户
    user = g.user
    try:
        pagination = user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT, False)
        follows = pagination.items
        total_page = pagination.pages
        current_page = pagination.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户收藏新闻信息失败')

    for followed_user in follows:
        followed_user.avatar_url_path = constants.QINIU_DOMIN_PREFIX + followed_user.avatar_url if followed_user.avatar_url else ''

    # 3. 使用模板
    return render_template('news/user_follow.html',
                           follows=follows,
                           total_page=total_page,
                           current_page=current_page)


# /user/follow
@profile_blu.route('/follow', methods=['POST'])
@login_required
def user_follow():
    '''
    用户关注
    :return:
    '''
    req_dict = request.json

    if not req_dict:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    user_id = req_dict.get('user_id')
    action = req_dict.get('action')
    
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if action not in ('do', 'undo'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        user_id = int(user_id)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型异常')

    try:
        follow_user = User.query.get(user_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='数据库查询被关注作者异常')

    if not follow_user:
        return jsonify(errno=RET.PARAMERR, errmsg='没有该作者信息')

    user = g.user
    # 根据action执行对应操作
    if action == 'do':
        if user not in follow_user.followers:
            follow_user.followers.append(user)
    elif action =='undo':
        if user in follow_user.followers:
            follow_user.followers.remove(user)
    else:
        return jsonify(errno=RET.PARAMERR, errmsg='参数非法')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='数据库操作失败')

    return jsonify(errno=RET.OK, errmsg='关注成功')


@profile_blu.route('/news')
@login_required
def user_news_list():
    user = g.user
    '''
        用户新闻发布详情页
    '''
    page = request.args.get('p', 1)
    if not page:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    try:
        page = int(page)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')

    try:
        pagenation = user.news_list.paginate(page, constants.USER_WRITE_MAX_NEWS, False)
        news_li = pagenation.items
        total_page = pagenation.pages
        current_page = pagenation.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询用户发布新闻分页错误')
    for i in news_li:
        if not i:
            print('news_li没有数据')
        print(i)
    return render_template('news/user_news_list.html',
                           news_li=news_li,
                           total_page=total_page,
                           current_page=current_page)


@profile_blu.route('/collection')
@login_required
def user_collection():
    '''
    用户详情页获取用户收藏新闻
    :return:
    '''
    user = g.user
    # 获取当前页数
    page = request.args.get('p',1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='；类型转换异常')
    try:
        pagenation = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_li = pagenation.items
        total_page = pagenation.pages
        current_page = pagenation.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.SERVERERR, errmsg='服务异常')

    return render_template('/news/user_collection.html',
                           news_li=news_li,
                           total_page=total_page,
                           current_page=current_page)


# /user/password
@profile_blu.route('/password', methods=['GET', 'POST'])
@login_required
def user_password():
    user = g.user
    '''
        用户详情页修改密码
    '''
    if request.method == 'GET':
        return render_template('/news/user_pass_info.html')
    else:
        req_dict = request.json
        if not req_dict:
            return jsonify(errno=RET.PARAMERR,errmsg='缺少参数')
        old_password = req_dict.get('old_password')
        new_password = req_dict.get('new_password')

        if not all([old_password,new_password]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

        # 校验密码
        if not user.check_passowrd(old_password):
            return jsonify(errno=RET.DBERR,errmsg='原始密码错误')

        user.password = new_password
        try:
            db.session.commit()
        except Exception as  e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR,errmsg='数据库操作失败')

        return jsonify(errno=RET.OK,errmsg='修改成功')


@profile_blu.route('/avatar',methods=['GET', 'POST'])
@login_required
def user_avatar():
    '''
    用户详情页设置头像
    :return:
    '''
    user = g.user
    if request.method == 'GET':
        return render_template('/news/user_pic_info.html', user=user)
    elif request.method == 'POST':
        file = request.files.get('avatar')
        if not file:
            return jsonify(errno=RET.PARAMERR, errmsg='文件缺失')
        try:
            key = storage(file.read())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR,errmsg='上传图片文件包错误')

        user.avatar_url = key

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库操作失败')

        avatar_url = constants.QINIU_DOMIN_PREFIX+user.avatar_url
        return jsonify(errno=RET.OK, errmsg='操作成功', avatar_url=avatar_url)


@profile_blu.route('/basic', methods=['GET', 'POST'])
@login_required
def user_basic():
    user = g.user

    if request.method == 'GET':
        return render_template('news/user_base_info.html', user=user)
    elif request.method == 'POST':
        # 接受修改用户信息参数
        req_dict = request.json
        if not req_dict :
            return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
        signature = req_dict.get('signature')
        nick_name = req_dict.get('nick_name')
        gender = req_dict.get('gender')

        if not all([signature, nick_name, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

        if gender not in ('MAN', 'WOMAN'):
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库操作失败')

        # 更新session
        session['nick_name'] = nick_name
        return jsonify(errno=RET.OK,errmsg='更新成功')


@profile_blu.route('')
@login_required
def get_user_profile():
    user = g.user
    return render_template('/news/user.html', user=user)