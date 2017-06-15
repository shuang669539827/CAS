# -*- coding: utf-8 -*-
from msg.models import Messages, Counter


def msg(request):
    if request.user.username:
        counter_obj, _ = Counter.objects.get_or_create(user=request.user)
        messages = Messages.objects.filter(accepter=request.user)
        return {'count': counter_obj.count, "messages": messages}
    else:
        return {}
