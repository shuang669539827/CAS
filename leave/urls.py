from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from .views import ApplyView, myholiday, notes, myapproval, result, manager, write_excel, notesearch, awayapply, down

urlpatterns = patterns('',
    url(r'^apply/$', login_required(ApplyView.as_view())),
    url(r'^myholiday/$', myholiday),
    url(r'^notes/$', notes),
    url(r'^myapproval/$', myapproval),
    url(r'^result/$', result),
    url(r'^manager/$', manager),
    url(r'^writecsv/$', write_excel),
    url(r'^notesearch/$', notesearch),
    url(r'^awayapply/$', awayapply),
    url(r'^down/$', down),
)