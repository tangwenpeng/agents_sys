from info import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel(object):
    '''创建时间和修改时间'''
    create_time = db.Column(db.DateTime, default=datetime.now)  # 创建的时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class AgentInfo(db.Model, BaseModel):
    '''代理申请信息'''
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增长
    name = db.Column(db.String(10), nullable=False)  # 姓名
    phone_number = db.Column(db.String(11))  # 手机号/联系方式
    province = db.Column(db.String(10))  # 省
    city = db.Column(db.String(10))  # 市
    county = db.Column(db.String(10))  # 县（区）
    original_wechat = db.Column(db.String(20), nullable=False)  # 原始微信号
    wechat_QR_code = db.Column(db.String(256))  # 粉丝截图
    collection_QR_code = db.Column(db.String(256))  # 用户收款二维码
    original_fans = db.Column(db.Integer)  # 原始粉丝数
    current_fans = db.Column(db.Integer)  # 当前粉丝数
    num_mobile = db.Column(db.Integer)  # 手机台数
    id_card_front = db.Column(db.String(256), nullable=True)  # 身份证正面照/非必填
    id_card_back = db.Column(db.String(256), nullable=True)  # 身份证反面照/非必填
    bank = db.Column(db.String(10), nullable=True)  # 银行
    card_number = db.Column(db.String(19), nullable=True)  # 银行卡号/非必填
    status = db.Column(db.String(1),default=0)  # 0表示待审核 1表示审核通过 2 审核驳回
    stat = db.relationship('Stat', backref='agent', uselist=False)  # 申请表和统计表一对一
    adorder = db.relationship('AdOrder', backref='agent', uselist=False)  # 申请表和接单表一对一
    is_delete = db.Column(db.String(1), default=0)  # 0正常 1删除

    def __repr__(self):
        return '<AgentInfo %r>' % self.name

    def to_dict(self):
        '''将对象转换为字典数据'''
        agent_dict = {
            'agent_id': self.id,
            'name': self.name,
            'province': self.province,
            'city': self.city,
            'county': self.county,
            'original_wechat': self.original_wechat,
            'wechat_QR_code': "http://pe9wqjxpq.bkt.clouddn.com/" + self.wechat_QR_code,
            'collection_QR_code': "http://pe9wqjxpq.bkt.clouddn.com/" + self.collection_QR_code,
            'original_fans': self.original_fans,
            'num_mobile': self.num_mobile,
            'phone_number': self.phone_number,
            'id_card_front': self.id_card_front,
            'id_card_back': self.id_card_back,
            'bank': self.bank,
            'card_number': self.card_number,
            'status': self.status,
        }
        return agent_dict


class Stat(db.Model, BaseModel):
    '''代理申请通过审核后加粉统计'''
    __tablename__ = 'stat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增长
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    today_fans = db.Column(db.Integer, nullable=False)  # 当天加粉数
    total_fans = db.Column(db.Integer)  # 累计粉丝数

    def __repr__(self):
        return '<Stat %r>' % self.total_fans

    def to_dict(self):
        '''将对象转换为字典数据'''
        stat_dict = {
            'stat_id': self.id,
            'agent_id': self.agent_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'today_fans': self.today_fans,
            'total_fans': self.total_fans,
        }
        return stat_dict


class AdOrder(db.Model, BaseModel):
    '''粉丝量到一定量然后广告接单'''
    __tablename__ = 'adorder'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增长
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    date_of_order = db.Column(db.DateTime, default=datetime.now)  # 接单日
    push_time = db.Column(db.DateTime)  # 推送广告时间/可以写多个时间
    ad_count = db.Column(db.Integer, nullable=False)  # 广告数量
    screenshots = db.Column(db.String(256))  # 截图
    amount = db.Column(db.Integer)  # 金额/单价
    check_out_date = db.Column(db.DateTime)  # 结算日
    state = db.Column(db.Boolean, default=0, index=True)  # 结算状态: 0表示未结算付款，1表示已结算付款
    remark = db.Column(db.String(50))  # 备注

    def __repr__(self):
        return '<AdOrder %r>' % self.id

    def to_dict(self):
        '''将对象转换为字典数据'''
        adorder_dict = {
            'adorder_id': self.id,
            'agent_id': self.agent_id,
            'date_of_order': self.date_of_order,
            'push_time': self.push_time,
            'ad_count': self.ad_count,
            'screenshots': self.screenshots,
            'amount': self.amount,
            'check_out_date': self.check_out_date,
            'state': self.state,
            'remark': self.remark,
        }
        return adorder_dict


class User(db.Model, BaseModel):
    '''用户表'''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增长
    username = db.Column(db.String(20))  # 用户名
    phone_number = db.Column(db.String(11))
    password = db.Column(db.String(20))  # 密码
    password_hash = db.Column(db.String(255))  # 密码哈希值
    position = db.Column(db.String(1),default=1)  # 1公司代理负责人 2财务 3注册代理 5:超管

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        '''在用户注册的时候使用，会调用generate_password_hash()并将password参数传给它，将它的返回值存储在列属性password_hash中'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''在用户验证的时候使用，会调用check_password_hash()并将数据库存储的哈希值和用户输入的密码传给它，并返回它的返回值，如果是True则表示密码正确'''
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        '''将对象转换为字典数据'''
        user_dict = {
            "user_id": self.id,
            "username": self.username,
            "password": self.password,
            "password_hash": self.password_hash,
            "position": self.position,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict



class Role(db.Model):
    '''角色'''
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(600))  # 角色权限列表
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    admins = db.relationship("Admin", backref='role')  # 管理员外键关系关联

    def __repr__(self):
        return "<Role %r>" % self.name


class Admin(db.Model):
    '''管理员'''
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员账号
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员，0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    adminlogs = db.relationship("Adminlog", backref='admin')  # 管理员登录日志外键关系关联
    oplogs = db.relationship("Oplog", backref='admin')  # 管理员操作日志外键关系关联

    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


class Adminlog(db.Model):
    '''管理员登录日志'''
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<Adminlog %r>" % self.id


class Oplog(db.Model):
    '''操作日志'''
    __tablename__ = "oplog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    reason = db.Column(db.String(600))  # 操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<Oplog %r>" % self.id
