# -*- coding: utf-8 -*-
import logging

from django.http import JsonResponse
from django.contrib.auth.models import User

from celerymail import send_msg

from models import Messages
from cas.models import Project

# Create your views here.
errlog = logging.getLogger('daserr')


def getmsg(request):
    subject = request.POST.get('subject', '')
    description = request.POST.get('description', '')
    app = request.POST.get('app', '')
    sender = request.POST.get('sender', '')
    accepter = request.POST.get('accepter', '')
    pushtype = request.POST.get('pushtype', '')
    dealtype = request.POST.get('dealtype', '')
    url = request.POST.get('url', '')

    accepter = accepter.split(',') if accepter else []

    if pushtype not in ['0', '1']:
        return JsonResponse({'code': 1, 'msg': 'pushtype必须为0,1'})

    if dealtype not in ['0', '1']:
        return JsonResponse({'code': 1, 'msg': 'dealtype必须为0,1'})

    if app not in [obj.name for obj in Project.objects.all()]:
        return JsonResponse({'code': 1, 'msg': 'app有误,项目不存在'})

    try:
        accepter_users = [User.objects.get(username=u) for u in accepter]
    except User.DoesNotExist:
        return JsonResponse({'code': 1, 'msg': 'accepter有误,接收者用户不存在'})

    if sender:
        try:
            sender_user = User.objects.get(username=sender)
        except User.DoesNotExist:
            return JsonResponse({'code': 1, 'msg': 'sender有误,发送者用户不存在'})
    else:
        sender_user = None

    msg = Messages(subject=subject, description=description, app=app,
                   sender=sender_user, pushtype=int(pushtype), dealtype=int(dealtype), url=url)
    msg.save(accepter_users)

    pro = Project.objects.get(name=app)

    if pushtype == '0':
        data = dict(agent_id=0, msg_type='text', remark='AlarmId|wer3sadasd28237', to_dep='', to_tag='',
                    to_user=','.join([obj.first_name for obj in accepter_users]), topic='dev_alarm',
                    Content="<a href='cas.100credit.cn/login/?next=/login/?service=%s&forward=%s'>%s %s %s</a>" % (
                        pro.url, msg.url, app, subject, description), project_name='CAS待办事项')

        send_msg.delay(data)

    return JsonResponse({'code': 0, 'id': msg.id})


def delmsg(request):

    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    pk = request.POST.get('id')
    app = request.POST.get('app')

    if not pk:
        return JsonResponse({'code': 1, 'msg': '缺少id'})
    if not app:
        return JsonResponse({'code': 1, 'msg': '缺少app'})
    logging.info("msg delete sender`s ip is :" + get_client_ip(request))
    try:
        obj = Messages.objects.get(pk=int(pk), app=app)
    except Messages.DoesNotExist:
        return JsonResponse({'code': 1, 'msg': 'id或app有误'})

    obj.delete()
    return JsonResponse({'code': 0})


def redirect_to(request):
    obj_id = request.GET.get('obj_id')
    obj = Messages.objects.get(pk=int(obj_id))
    if obj.dealtype == 0:
        obj.delete()
    return JsonResponse({'code': 0, 'url': obj.get_absolute_url()})
