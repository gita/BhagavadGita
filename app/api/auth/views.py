from datetime import datetime, timedelta

from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_rq import get_queue
from werkzeug.security import gen_salt

from . import auth
from ... import csrf, db, oauth
from ...models import Client, Grant, Token, User
from .forms import UserForm


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@auth.route('/', methods=('GET', 'POST'))
def home():
    form = UserForm()
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(email=username).first()
        current_app.logger.info("RadhaKrishnaHanuman")
        current_app.logger.info(user)
        if not user:
            user = User(email=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        return redirect('/krishna/')
    user = current_user()
    return render_template('auth/home.html', user=user, form=form)


@auth.route('/client')
def client():
    user = current_user()
    if not user:
        return redirect('/')
    item = Client(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        _redirect_uris=' '.join([
            'http://localhost:8000/authorized',
            'http://127.0.0.1:8000/authorized',
            'http://127.0.1:8000/authorized',
            'http://127.1:8000/authorized',
        ]),
        _default_scopes='email',
        user_id=user.id,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(
        client_id=item.client_id,
        client_secret=item.client_secret,
    )


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user(),
        expires=expires)
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(
        client_id=request.client.client_id, user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@auth.route('/oauth/token', methods=['POST'])
@oauth.token_handler
@csrf.exempt
def access_token():
    """
    Send client credentials and get an access token.
    ---
    tags:
    - auth
    parameters:
    - name: client_id
      in: formData
      required: 'True'
      type: 'string'
      description: "Your app's client_id. Get from API dashboard."
    - name: client_secret
      in: formData
      required: 'True'
      type: 'string'
      description: "Your app's client_secret. Get from API dashboard."
    - name: grant_type
      in: formData
      required: 'True'
      type: 'string'
      default: 'client_credentials'
      description: "Grant Type."
    - name: scope
      in: formData
      required: 'True'
      type: 'string'
      default: verse chapter
      description: "The resources that you would like to access."
    consumes:
    - application/x-www-form-urlencoded
    produces:
    - application/json
    responses:
      200:
        description: 'Success: Everything worked as expected.'
        examples:
          - access_token: "cN31b7gClnImuQg8OeMGsUWYGsA0we"
            token_type: "Bearer"
            scope: "email"
      400:
        description: 'Bad Request: The request was unacceptable due to wrong parameter(s).'
      401:
        description: 'Unauthorized: Invalid access_token used.'
      402:
        description: 'Request Failed.'
      500:
        description: 'Server Error: Something went wrong on our end.'

    """
    return None


@auth.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = current_user()
    if not user:
        return redirect('/krishna/')
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('auth/authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@auth.route('/api/me')
@oauth.require_oauth()
def me():
    return jsonify("RadhaKrishna")
