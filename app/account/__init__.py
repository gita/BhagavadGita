from flask import Blueprint
from flask_login import current_user
from .. import db


account = Blueprint('account', __name__)

from . import views  # noqa
