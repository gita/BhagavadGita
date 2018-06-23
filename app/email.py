import os
from flask_mail import Message
from . import mail
from flask import current_app, render_template
import jinja2
import boto3
from botocore.exceptions import ClientError


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


def send_shloka(email_list, subject, template, **kwargs):
    # for email in email_list:
    SENDER = "Bhagavad Gita Daily <shloka@bhagavadgita.io>"
    RECIPIENT = email_list[0]
    AWS_REGION = "us-east-1"

    SUBJECT = "Bhagavad Gita - " + subject

    BODY_TEXT = render_without_context(
        template + '.txt', unsubscribe="https://bhagavadgita.io/shloka-unsubscribe/" + email_list[0], **kwargs)

    BODY_HTML = render_without_context(
        template + '.html', unsubscribe="https://bhagavadgita.io/shloka-unsubscribe/" + email_list[0], **kwargs)

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
