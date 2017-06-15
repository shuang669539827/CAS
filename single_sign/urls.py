#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = [
    url(r'', include('cas.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dinner/', include('dinner.urls')),
    url(r'^leave/', include('leave.urls')),
    url(r'^yunpan/', include('mypan.urls')),
    url(r'^cms/', include('cms.urls')),
    url(r'^msg/', include('msg.urls')),
    url(r'^check/', include('checkin.urls')),
]
