from flask import Blueprint
from flask_login import current_user
from ... import db

auth = Blueprint('auth', __name__)

from . import views  # noqa
