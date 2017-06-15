from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import TotalView, CancelView, OrderView, FoodView, DelFoodView, ShowFoodView, AddFoodView, Index, OrderList


urlpatterns = patterns('',
    url(r'^$', Index),
    url(r'^orders/$', login_required(OrderView.as_view())),
    url(r'^cancel/$', login_required(CancelView.as_view())),
    url(r'^total/$', login_required(TotalView.as_view())),
    url(r'^food/$', login_required(FoodView.as_view())),
    url(r'^food/del/$', login_required(DelFoodView.as_view())),
    url(r'^food/show/$', login_required(ShowFoodView.as_view())),
    url(r'^food/add/$', login_required(AddFoodView.as_view())),
    url(r'^notes/$', login_required(OrderList.as_view())),

)
