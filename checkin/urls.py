# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import CheckShow, CheckDetail, CheckTotalView, CheckTotalDetail, grade


urlpatterns = [
    url(r'^list/$', CheckShow.as_view(), name='check_list'),
    url(r'^(?P<pk>\d+)/detail/$', CheckDetail.as_view(), name='check_detail'),
    url(r'^total/list/$', CheckTotalView.as_view(), name='check_total_list'),
    url(r'^(?P<pk>\d+)/total/deatil/$', CheckTotalDetail.as_view(), name='check_total_detail'),
    url(r'^(\d+)/grade/$', grade, name='grade'),
]
