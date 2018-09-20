import redis
import logging
import pymysql
# 添加项目的配置类


class Config(object):
    DEBUG = True
    # 设置csrf秘钥
    SECRET_KEY = 'OXONI02x43p3W3hhHMW8KXOR8PJJd+Kw9JB7aeAVVoHeWKSqOWgOgk9yplTZhi3D'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@127.0.0.1:3306/proxy'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 定义redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 配置session存放的数据库
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST , REDIS_PORT)
    # 设置session中的值做加密处理
    SESSION_USE_SIGNER = True


class DevelopementConfig(Config):
    DEBUG = True
    LOG_LEVEL=logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

config_dict = {
    'developmentConfig': DevelopementConfig,
    'productionConfig': ProductionConfig
}
