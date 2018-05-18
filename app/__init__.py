import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_assets import Environment
from flask_wtf import CsrfProtect
from flask_compress import Compress
from flask_rq import RQ
from app.lib.flask_oauthlib.provider import OAuth2Provider
from flask_restful import Api
from flask_babel import Babel
from app.lib.flask_oauthlib.client import OAuth
from elasticsearch import Elasticsearch

from config import config
from .assets import app_css, app_js, vendor_css, vendor_js

from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
csrf = CsrfProtect()
compress = Compress()
csrf = CsrfProtect()
oauth = OAuth2Provider()
oauthclient = OAuth()
babel = Babel()

github_blueprint = make_github_blueprint(client_id=os.environ.get('GITHUB_KEY'), client_secret=os.environ.get('GITHUB_SECRET'))
google_blueprint = make_google_blueprint(client_id=os.environ.get('GOOGLE_KEY'),
                                         client_secret=os.environ.get('GOOGLE_SECRET'),
                                         scope=["profile", "email"], authorized_url="https://")
facebook_blueprint = make_facebook_blueprint(
    client_id=os.environ.get('FACEBOOK_KEY'), client_secret=os.environ.get('FACEBOOK_SECRET'))

es = Elasticsearch(
    [os.environ.get('ES_URL') or 'ES_URL'],
    http_auth=(os.environ.get('ES_USERNAME') or 'ES_USERNAME', os.environ.get('ES_PASSWORD') or 'ES_PASSWORD'),
    scheme="https"
)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'


def create_app(config_name):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it

    config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    oauthclient.init_app(app)
    RQ(app)
    api = Api(app)
    babel.init_app(app)

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from .api.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.api.docs import docs as docs_blueprint
    app.register_blueprint(docs_blueprint)

    app.register_blueprint(github_blueprint, url_prefix='/github_login')
    app.register_blueprint(google_blueprint, url_prefix='/google_login')
    app.register_blueprint(facebook_blueprint, url_prefix='/facebook_login')

    from flasgger import APISpec, Schema, Swagger, fields

    spec = APISpec(
        title='Bhagavad Gita API',
        version='1.0.0',
        plugins=[
            'apispec.ext.flask',
            'apispec.ext.marshmallow',
        ],
    )

    app.config['SWAGGER'] = {'title': 'Bhagavad Gita API', 'uiversion': 3}

    swagger = Swagger(
        app,
        template={
            'swagger': '2.0',
            'info': {
                'title': 'Bhagavad Gita API',
                'version': '1.0'
            }
        })

    from app.api.v1.verse import VerseList, VerseListByChapter, VerseByChapter
    from app.api.v1.chapter import Chapter, ChapterList

    verse_list_view = VerseList.as_view('VerseList')
    app.add_url_rule('/api/v1/verses', view_func=verse_list_view)

    verse_list_chapter_view = VerseListByChapter.as_view('VerseListChapter')
    app.add_url_rule(
        '/api/v1/chapters/<int:chapter_number>/verses',
        view_func=verse_list_chapter_view)

    verse_chapter_view = VerseByChapter.as_view('VerseChapter')
    app.add_url_rule(
        '/api/v1/chapters/<int:chapter_number>/verses/<string:verse_number>',
        view_func=verse_chapter_view)

    chapter_view = Chapter.as_view('Chapter')
    app.add_url_rule(
        '/api/v1/chapters/<int:chapter_number>', view_func=chapter_view)

    chapter_list_view = ChapterList.as_view('ChapterList')
    app.add_url_rule('/api/v1/chapters', view_func=chapter_list_view)

    with app.test_request_context():
        spec.add_path(view=verse_list_view)
        spec.add_path(view=verse_list_chapter_view)
        spec.add_path(view=verse_chapter_view)
        spec.add_path(view=chapter_view)
        spec.add_path(view=chapter_list_view)

    return app
