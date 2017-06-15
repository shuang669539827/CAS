from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from views import (index, LoginView, validate, proinfo, prolist, enterinfo,
                   Alterpro, repasswd, applypermres, logout, prosearch,
                   get_vercode, re_passwd, alterinfo, userprojectlist, userprojectsearch,
                   addrole, userprojectalter, userprojectdel, addprojectrole, docs,
                   applyperm, applypermlist, searchuser, searchdepartment, radar)

urlpatterns = [
    url(r'^login/$', LoginView.as_view()),
    url(r'^$', index),
    url(r'^index/$', index),
    url(r'^docs/$', docs),
    url(r'^validate/$', validate),
    url(r'^proinfo/$', proinfo),
    url(r'^logout/$', logout),
    url(r'^enterinfo/$', enterinfo),
    url(r'^prolist/$', prolist),
    url(r'^pro/alter/(?P<pro_id>[0-9]+)$', login_required(Alterpro.as_view())),
    url(r'^pro/search/$', prosearch),
    url(r'^repasswd/$', repasswd),
    url(r'^alterinfo/$', alterinfo),
    url(r'^userprojectlist/$', userprojectlist),
    url(r'^userproject/search/$', userprojectsearch),
    url(r'^userproject/alter/$', userprojectalter),
    url(r'^userproject/add/$', addrole),
    url(r'^projectrole/add/$', addprojectrole),
    url(r'^userproject/del/$', userprojectdel),
    url(r'^get_vercode/$', get_vercode),
    url(r'^re_passwd/$', re_passwd),
    url(r'^applyperm/$', applyperm),
    url(r'^applypermlist/$', applypermlist),
    url(r'^applypermres/$', applypermres),
    url(r'^search/user/$', searchuser),
    url(r'^search/department/$', searchdepartment),
    url(r'^radar/getData/v1/$', radar),
]
