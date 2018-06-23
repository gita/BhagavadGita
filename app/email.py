import os
from flask_mail import Message
from . import mail
from flask import current_app, render_template
import jinja2


def send_email(recipient, subject, template, **kwargs):
    msg = Message(
        current_app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=current_app.config['EMAIL_SENDER'],
        recipients=[recipient])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


def render_without_context(template_name, **context):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('app')
    )
    template = env.get_template(template_name)
    return template.render(**context)


#from manage import app
def send_shloka(email_list, subject, template, **kwargs):
    for email in email_list:
        msg = Message(
            "Bhagavad Gita -" + ' ' + subject,
            sender='Bhagavad Gita Daily <{email}>'.format(email="contact@bhagavadgita.io"),
            recipients=[email])
        msg.body = render_without_context(
            template + '.txt', unsubscribe="https://bhagavadgita.io/shloka-unsubscribe/" + email, **kwargs)
        msg.html = render_without_context(
            template + '.html', unsubscribe="https://bhagavadgita.io/shloka-unsubscribe/" + email, **kwargs)
        with app.app_context():
            mail.send(msg)
