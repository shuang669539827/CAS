from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import (ApplyView, myholiday, LeaveNotes, progress_transition,
                    manager, write_excel, notesearch, force_stop,
                    down, ApprovaledList, ApprovalingList, managersearch2,
                    managersearch3, write_approvaled, write_approvaling,
                    NoteDetail)

urlpatterns = [
    url(r'^apply/$', login_required(ApplyView.as_view())),
    url(r'^myholiday/$', myholiday, name='holiday'),
    url(r'^notes/$', LeaveNotes.as_view(), name='leave-notes'),
    url(r'^manager1/$', manager),
    url(r'^manager2/$', ApprovaledList.as_view(), name='manager2'),
    url(r'^manager3/$', ApprovalingList.as_view(), name='manager3'),
    # url(r'^managersearch2/$', managersearch2),
    # url(r'^managersearch3/$', managersearch3),
    url(r'^writecsv/$', write_excel),
    url(r'^notesearch/$', notesearch),
    url(r'^down/$', down, name='downfile'),
    url(r'^down_approvaled/$', write_approvaled),
    url(r'^down_approvaling/$', write_approvaling),
    url(r'^(?P<pk>[0-9]+)/detail/$', NoteDetail.as_view(), name='note_detail'),
    url(r'^(\d+)/transaction/$', progress_transition, name='leave_progress'),
    url(r'^(\d+)/stop/$', force_stop, name='leave_stop'),
]
