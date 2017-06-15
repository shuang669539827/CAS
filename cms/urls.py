# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import (
    TaskDetail, TaskList, TaskDelete, TaskCreate, add_comment, filing,
    progress_transition, force_stop, down, add_party, revoke, modify
)


urlpatterns = [
    url(r'^list/$', TaskList.as_view(), name='task_list'),
    url(r'^create/$', TaskCreate.as_view(), name='task_create'),
    url(r'^(?P<pk>[0-9]+)/detail/$', TaskDetail.as_view(), name='task_detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', TaskDelete.as_view(), name='task_delete'),
    url(r'^(\d+)/add/comment/$', add_comment, name='add_comment'),
    url(r'^(\d+)/transaction/$', progress_transition, name='progress_transition'),
    url(r'^(\d+)/stop/$', force_stop, name='force_stop'),
    url(r'^down/(?P<pk>(\d+))/$', down, name='down_file'),
    url(r'^add/partyfirst/$', add_party),
    url(r'^add/partysecond/$', add_party),
    url(r'^(\d+)/revoke/$', revoke, name='revoke'),
    url(r'^(\d+)/modify/$', modify, name='modify'),
    url(r'^filing/$', filing, name='filing'),
]
