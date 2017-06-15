# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import (
    getmsg, delmsg, redirect_to
)

urlpatterns = [
    url(r'^send/$', getmsg),
    url(r'^delete/$', delmsg),
    url(r'^redirect/$', redirect_to, name='redirect_to'),
]
