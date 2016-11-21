from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import TotalView, CancelView, OrderView, FoodView, DelFoodView, ShowFoodView, AddFoodView, Index

import time


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Eat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', Index),
    url(r'^orders/$', login_required(OrderView.as_view())),
    url(r'^cancel/$', login_required(CancelView.as_view())),
    url(r'^total/$', login_required(TotalView.as_view())),
    # url(r'^type/$', login_required(TypeView.as_view())),
    #url(r'^type/del/$', login_required(DelTypeView.as_view())),
    #url(r'^type/show/$', login_required(ShowTypeView.as_view())),
    #url(r'^type/add/$', login_required(AddTypeView.as_view())),
    url(r'^food/$', login_required(FoodView.as_view())),
    url(r'^food/del/$', login_required(DelFoodView.as_view())),
    url(r'^food/show/$', login_required(ShowFoodView.as_view())),
    url(r'^food/add/$', login_required(AddFoodView.as_view())),
)
