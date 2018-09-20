#coding=utf-8
from flask import Blueprint

#创建新闻模块蓝图对象
admin_blue = Blueprint('admin',__name__)

#导入视图模块
from . import views