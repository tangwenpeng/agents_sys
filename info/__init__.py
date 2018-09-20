import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session

from config import config_dict

db = SQLAlchemy()
redis_store = None


def setup_logging(log_level):
    logging.basicConfig(level=log_level)  # 调试debug级
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=100 * 1024 * 1024, backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


# 加载配置
def create_app(configName):
    app = Flask(__name__)

    config_cls = config_dict[configName]
    setup_logging(config_cls.LOG_LEVEL)
    app.config.from_object(config_cls)
    global redis_store
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)
    db.init_app(app)

    # 为flask项目开启csrf保护
    # CSRFProtect(app)

    # 在服务器产生csrf_token
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 配置浏览器session存放
    Session(app)

    # 定义模板过滤器
    from info.utils.commons import do_rank_class, do_status_change
    app.add_template_filter(do_rank_class, 'rank_class')
    app.add_template_filter(do_status_change, 'status_change')

    # 404
    from info.utils.commons import login_user_data
    # @app.errorhandler(404)
    # @login_user_data
    # def handler_not_found_page(e):
    #     return render_template('news/404.html')

    from info.modules.index import index_blue
    from info.modules.passport import passport_blu
    from info.modules.profile import profile_blu
    from info.modules.admin import admin_blue

    # flaskapp注册自定义index模块蓝图
    app.register_blueprint(index_blue)
    # 注册passsport蓝图
    app.register_blueprint(passport_blu, url_prefix='/passport')
    # 新闻蓝图
    # 用户蓝图
    app.register_blueprint(profile_blu, url_prefix='/user')

    # 管理员模块蓝图
    app.register_blueprint(admin_blue, url_prefix='/admin')

    return app
