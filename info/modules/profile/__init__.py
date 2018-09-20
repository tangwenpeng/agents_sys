from flask import Blueprint
profile_blu = Blueprint('profile', __name__)

from . import views