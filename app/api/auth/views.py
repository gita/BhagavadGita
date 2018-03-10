from datetime import datetime, timedelta

from flask import session

from . import auth
from ... import csrf, db, oauth
from ...models import Client, Grant, Token, User


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


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
