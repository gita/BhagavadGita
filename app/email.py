import os
from flask_mail import Message
from . import mail
from flask import current_app, render_template


def send_email(recipient, subject, template, **kwargs):
    msg = Message(
        current_app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=current_app.config['EMAIL_SENDER'],
        recipients=[recipient])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)    
    mail.send(msg)
