#coding=utf-8
import datetime
import random

from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from info import create_app,db,models
from info.models import User

app = create_app('developmentConfig')
# app = create_app('productionConfig')
# 创建管理类对象
manager = Manager(app)
Migrate(app, db)
# 添加命令
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    """创建管理员用户"""
    if not all([name, password]):
        print('参数不足')
        return
    from info.models import User
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()
'''
def add_test_users():
    users = []
    now = datetime.datetime.now()
    for num in range(997, 10000):
        try:
            user = User()
            user.nick_name = "%010d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            user.create_time = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    with app.app_context():
        db.session.add_all(users)
        db.session.commit()
    print ('OK')
'''

if __name__ == '__main__':
    manager.run()
    #add_test_users()