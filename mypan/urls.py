from django.conf.urls import url

import views


urlpatterns = [
    url(r'^$', views.home),
    url(r'^uploadfile/$', views.uploadfile),
    url(r'^downloadfile/$', views.download_file),
    url(r'^showfile/$', views.cmd_ls),
    url(r'^createfile/$', views.create_file),
    url(r'^deletefile/$', views.delete_file),
    url(r'^rename/$', views.rename),

]
