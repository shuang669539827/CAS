# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import smtplib
import requests
import datetime
import json
import math

from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

from celery import current_app as app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(name='celerymail.send_html_mail', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def send_html_mail_task(subject, content, recipient_list, filepath=None):
    logger.info('celerymail.send_html_mail - %s - %s' % (subject, recipient_list))
    try:
        msg = EmailMessage(subject, content, settings.EMAIL_HOST_USER, recipient_list)
        msg.content_subtype = "html"
        if filepath:
            msg.attach_file(filepath)
        msg.send()
    except smtplib.SMTPRecipientsRefused:
        user = User.objects.get(email=recipient_list[0])
        content = user.first_name + ":" + user.email + "邮箱有误，请修改."
        msg = EmailMessage(
                "CAS系统假期申请,申请人邮箱错误", content, 'cas@100credit.com',
                ['cas@100credit.com']
            )
        msg.content_subtype = "html"
        msg.send()


@app.task(name='celerymail.send_msg', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def send_msg(msg):
    logger.info('celerymail.send_msg %s' % json.dumps(msg))
    try:
        requests.post('http://192.168.23.124:8970', data=json.dumps(msg))
    except requests.ConnectionError:
        pass
