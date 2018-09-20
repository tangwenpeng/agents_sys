#coding=utf-8
from flask import Blueprint

#创建新闻模块蓝图对象
index_blue = Blueprint('index',__name__)

#导入视图模块
from . import views