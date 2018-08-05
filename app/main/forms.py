from flask import url_for
from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length


class ContactForm(Form):
    name = StringField(
        'Your name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Your Email', validators=[InputRequired(),
                                  Length(1, 64),
                                  Email()])
    subject = StringField('Subject', validators=[Length(1, 64)])
    message = TextAreaField(
        'Message', validators=[InputRequired(),
                               Length(1, 200)])
    submit = SubmitField('Send')


class ShlokaForm(Form):
    meaning = TextAreaField('Meaning')
    submit = SubmitField('Send')
