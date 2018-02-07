from flask import url_for
from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import (BooleanField, PasswordField, StringField,
                            SubmitField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from ...models import User


class UserForm(Form):
    username = StringField(
        'Username', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Log in')


class AuthorizationForm(Form):
    client_id = StringField()
    scope = StringField()
    response_type = StringField()
    redirect_uri = StringField()
    state = StringField()
    confirm = SubmitField('Confirm')
