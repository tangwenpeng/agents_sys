# coding=utf-8

# 创建passport蓝图模块
from flask import Blueprint
passport_blu = Blueprint('passport',__name__)
# 引入视图
from . import views