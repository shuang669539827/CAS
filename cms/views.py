# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import os
import re
import urlparse

from django.db.models import Q
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, TemplateView
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotFound, Http404, StreamingHttpResponse
from django.utils.http import urlencode
from django.db import IntegrityError
from django.conf import settings

from celerymail import send_html_mail
from single_sign.maxin import LoginRequiredMixin
from workflow.models import Transition, State, WorkflowHistory
from workflow.exceptions import WorkflowException
from msg.models import Messages

from .models import (
    Task, TaskFile, Partyfirst, Partysecond
)


logger = logging.getLogger('daserr')


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    paginate_by = 20
    context_object_name = 'tasks'
    template_name = 'cms-tasklist.html'

    def get_queryset(self):
        queryset = super(TaskList, self).get_queryset()
        user = self.request.user
        self.show = self.request.GET.get('show', 'self').lower()  # self: 我的任务; all: 所有任务
        self.my = self.request.GET.get('my', 'doing').lower()
        self.state = self.request.GET.get('state', 'doing').lower()
        if self.show != 'all':
            queryset = queryset.filter(workflowactivity__participants__user=user)
            if self.my == 'doing':
                queryset = queryset.exclude(~Q(workflowactivity__current_state__users=user), label='')\
                                .exclude(~Q(create_by=user), label='start')\
                                .exclude(label='end')\
                                .exclude(~Q(create_by__pro__department__user=user), label='department')

            else:
                queryset = queryset.exclude(workflowactivity__current_state__users=user, label='')\
                                .exclude(create_by=user, label='start')\
                                .exclude(create_by__pro__department__user=user, label='department')
        else:
            if self.state == 'doing':
                queryset = queryset.filter(workflowactivity__current_state__is_end_state=False)
            elif self.state == 'did':
                queryset = queryset.filter(workflowactivity__current_state__is_end_state=True, filing=False)
            else:
                queryset = queryset.filter(workflowactivity__current_state__is_end_state=True, filing=True)
            # trans = Transition.objects.filter(label__in=['xz1', 'xz2', 'ceo', 'cfo']).select_related().values_list('users__username').distinct()
            # users = [tran[0] for tran in trans]
            # if user.username not in users:
            #     raise Http404
        return queryset.select_related('workflowactivity', 'workflowactivity__current_state').all()

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        # trans = Transition.objects.filter(label__in=['xz1', 'xz2', 'ceo', 'cfo']).values_list('users__username').distinct()
        # users = [tran[0] for tran in trans]
        """前三次传输(通过,拒绝)的权限需要赋予任何人"""
        try:
            startran = Transition.objects.filter(label='start')
            for t in startran:
                t.users.add(self.request.user)
                t.save()
            departtran = Transition.objects.filter(label='department')
            for r in departtran:
                r.users.add(self.request.user)
                r.save()
        except (Transition.DoesNotExist, Transition.MultipleObjectsReturned):
            logger.info('transition`s label is not exits')
        try:
            starstat = State.objects.get(label='start')
            starstat.users.add(self.request.user)
            starstat.save()
            departstat = State.objects.get(label='department')
            departstat.users.add(self.request.user)
            departstat.save()
        except (State.DoesNotExist, State.MultipleObjectsReturned):
            logger.info('State`s label is not exits')

        # if self.request.user.username in users:
        #     context['perm'] = True
        # else:
        #     context['perm'] = False
        context['partyfirst'] = Partyfirst.objects.all().distinct()
        context['partysecond'] = Partysecond.objects.all().distinct()
        context['show'] = self.show
        context['my'] = self.my
        context['state'] = self.state
        context['extra_url_param'] = urlencode({'show': self.show, 'my': self.my, 'state': self.state})
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'cms-taskdetail.html'

    def getlasthis(self, his):
        his = his
        if not his[0].transition:
            return self.getlasthis(his[1:])
        else:
            return his[0]

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        # 定义可以执行操作的人
        his = list(self.object.workflowactivity.history.all())
        lasthis = self.getlasthis(his)
        if lasthis.transition.label == 'department':
            if self.object.total or self.object.univalent:
                context['transitions'] = self.object.has_perm_use_transitions(self.request.user).exclude(label='fw2')
            else:
                context['transitions'] = self.object.has_perm_use_transitions(self.request.user).exclude(label='fw1')

        elif lasthis.transition.label == 'ceo':
            if self.object.total or self.object.univalent:
                context['transitions'] = self.object.has_perm_use_transitions(self.request.user).exclude(label='xz2')
            else:
                context['transitions'] = self.object.has_perm_use_transitions(self.request.user).exclude(label='xz1')
        else:
            context['transitions'] = self.object.has_perm_use_transitions(self.request.user)
        context['partyfirst'] = Partyfirst.objects.all()
        context['partysecond'] = Partysecond.objects.all()
        return context


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('task_list')

    @method_decorator(permission_required('task.delete_task', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(TaskDelete, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.content_object.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class TaskCreate(LoginRequiredMixin, TemplateView):
    success_url = reverse_lazy('task_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TaskCreate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotFound

        partyfirst_id = request.POST.get('contact-partyfirst', '')
        partysecond_id = request.POST.get('contact-partysecond', '')
        name = request.POST.get('contact-name', '')
        note = request.POST.get('contact-note', '')
        univalent = request.POST.get('contact-univalent', None)
        total = request.POST.get('contact-total', None)
        files = request.FILES.getlist('attachment')

        if total:
            try:
                total = float(total) if float(total) > 0 else None
            except ValueError:
                return JsonResponse({'msg': '请输入正数!'})
        else:
            total = None

        if univalent:
            try:
                univalent = float(univalent) if float(univalent) > 0 else None
            except ValueError:
                return JsonResponse({'msg': '请输入正数!'})
        else:
            univalent = None

        if not (name and note):
            return JsonResponse({'msg': '缺少必填信息'})

        if not (partyfirst_id and partysecond_id):
            return JsonResponse({'msg': '缺少甲方或乙方'})

        partyfirst = Partyfirst.objects.get(pk=int(partyfirst_id))
        partysecond = Partysecond.objects.get(pk=int(partysecond_id))

        task = Task(partyf=partyfirst,
                    partys=partysecond,
                    name=name,
                    univalent=univalent,
                    total=total,
                    note=note,
                    create_by=request.user
                    )
        task.save()

        for f in files:
            TaskFile.objects.create(file=f, task=task)

        task.create(request.user)

        return JsonResponse({'msg': '0'})


@login_required
def progress_transition(request, task_id):
    if request.method == 'POST':
        transaction_id = 1
        partyfirst_id = request.POST.get('contact-partyfirst', '')
        partysecond_id = request.POST.get('contact-partysecond', '')

        name = request.POST.get('contact-name', '')
        note = request.POST.get('contact-note', '')
        univalent = request.POST.get('contact-univalent')
        total = request.POST.get('contact-total')
        files = request.FILES.getlist('attachment')

        new_note = request.POST.get('new-note', '')

        if total:
            try:
                total = float(total) if float(total) > 0 else None
            except ValueError:
                return JsonResponse({'msg': '请输入正数!'})
        else:
            total = None

        if univalent:
            try:
                univalent = float(univalent) if float(univalent) > 0 else None
            except ValueError:
                return JsonResponse({'msg': '请输入正数!'})
        else:
            univalent = None

        if transaction_id is None:
            return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({'msg': 'Task <%s> does not exist' % task_id})
        try:
            transaction = Transition.objects.get(id=int(transaction_id))
        except Transition.DoesNotExist:
            return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})

        try:
            partyfirst = Partyfirst.objects.get(pk=int(partyfirst_id))
            partysecond = Partysecond.objects.get(pk=int(partysecond_id))
            task.partyf = partyfirst
            task.partys = partysecond
            task.name = name
            task.univalent = univalent
            task.total = total
            task.note = note
            task.save()
            for f in files:
                TaskFile.objects.create(file=f, task=task)
            task.workflowactivity.progress(transaction, request.user, note='重新提交：' + new_note)
        except WorkflowException as e:
            return JsonResponse({'msg': str(e)})

    else:
        transaction_id = request.GET.get('transId')
        reason = request.GET.get('reason', '')
        """退回再次申请"""

        if transaction_id is None:
            return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({'msg': 'Task <%s> does not exist' % task_id})
        try:
            transaction = Transition.objects.get(id=int(transaction_id))
        except Transition.DoesNotExist:
            return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})
        try:
            if reason:
                task.workflowactivity.progress(transaction, request.user, note=reason)
            else:
                task.workflowactivity.progress(transaction, request.user)
        except WorkflowException as e:
            return JsonResponse({'msg': str(e)})

    return JsonResponse({'msg': 0})


@login_required
@csrf_exempt
def add_comment(request, task_id):
    note = request.POST.get('note', '')
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'msg': 'Task <%s> Does not exist' % task_id})

    if note.strip():
        try:
            task.workflowactivity.add_comment(request.user, note)
        except WorkflowException as e:
            return JsonResponse({'msg': str(e)})

    task.workflowactivity.add_participant(request.user)
    return JsonResponse({'msg': 0})


@login_required
@csrf_exempt
def force_stop(request, task_id):
    reason = request.GET.get('reason', '')

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'msg': 'Task <%s> Does not exist' % task_id})

    try:
        task.workflowactivity.force_stop(request.user, reason)
    except WorkflowException as e:
        return JsonResponse({'msg': str(e)})

    return JsonResponse({'msg': 0})


@login_required
def down(request, **kwargs):
    pk = kwargs.get('pk')
    tf = TaskFile.objects.get(pk=pk)
    path = tf.file.path
    _, name = os.path.split(tf.file.path)

    def file_iterator(chunk_size=512):
        with open(path) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator())
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(name).encode('utf-8')
    return response


def add_party(request):
    name = request.GET.get('name', '')
    if not name:
        return JsonResponse({'msg': '缺少必填信息'})
    if re.match(r'^/cms/add/partyfirst/$', request.path):
        try:
            Partyfirst.objects.create(name=name)
        except IntegrityError:
            return JsonResponse({'msg': '该名称已存在'})
    elif re.match(r'^/cms/add/partysecond/$', request.path):
        try:
            Partysecond.objects.create(name=name)
        except IntegrityError:
            return JsonResponse({'msg': '该名称已存在'})
    return JsonResponse({'msg': 0})


def revoke(request, task_id):
    revoke_note = request.GET.get('revoke_note')
    if not revoke_note:
        return JsonResponse({'msg': '请填写撤回原因'})

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'msg': '该合同不存在'})
    message = '<h3>{title}</h3>' \
              '<a href="{link}">合同名称： {name}</a>' \
              '<p>申请人： {applicant}</p>' \
              '<p>当前状态： {state}</p>' \
              '<p>描述： {desc}</p>' \
        .format(
            title='CAS - 合同提醒',
            name=task.name,
            link=urlparse.urljoin(settings.MAIN_DOMAIN, task.get_absolute_url()),
            applicant=task.workflowactivity.created_by.get_full_name(),
            state='待修改',
            desc=task.note
        )

    mail_list = [task.workflowactivity.created_by.email]
    if task.workflowactivity.current_state.label == 'department':
        mail_list.append(task.workflowactivity.created_by.pro.department.user.email)
    else:
        for u in task.workflowactivity.current_state.users:
            mail_list.append(u.email)

    send_html_mail('CAS - 合同提醒', message, mail_list)

    current_state = State.objects.filter(pk=1).first()
    task.workflowactivity.current_state = current_state
    task.workflowactivity.save()

    wh = WorkflowHistory(
        workflowactivity=task.workflowactivity,
        state=current_state,
        log_type=WorkflowHistory.COMMENT,
        note='撤销：'+revoke_note,
        created_by=request.user,
    )
    wh.save(user=request.user)

    task.label = 'start'
    task.save()

    try:
        Messages.objects.get(app='采购合同审批', mid=task.pk).delete()
    except Messages.DoesNotExist:
        pass

    msg = Messages(subject=task.name, description='由 %s 提交的合同' % task.workflowactivity.created_by.first_name,
                   app='采购合同审批', sender=task.workflowactivity.created_by, mid=task.pk, url='/cms/list/')
    msg.save(accepter=[request.user])

    return JsonResponse({'msg': 0})


def modify(request, task_id):
    modify_note = request.POST.get('modify_note')
    modify_file = request.FILES.getlist('modify_file')

    if not modify_note:
        return JsonResponse({'msg': '请填写备注信息'})
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'msg': '该合同不存在'})

    wh = WorkflowHistory(
        workflowactivity=task.workflowactivity,
        log_type=WorkflowHistory.COMMENT,
        state=task.workflowactivity.current_state,
        note=modify_note,
        created_by=request.user,
    )
    wh.save(user=request.user)

    for f in modify_file:
        TaskFile.objects.create(file=f, task=task)
    return JsonResponse({'msg': 0})


@login_required
def filing(request):
    task_id = request.POST.get('filing_task_id')
    filing_note = request.POST.get('filing_note')
    filing_file = request.FILES.getlist('filing_file')

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'msg': '该合同不存在'})

    if not filing_note:
        return JsonResponse({'msg': '请填写备注信息'})

    for f in filing_file:
        _, ext = os.path.splitext(f.name)
        if ext not in ['.jpg', '.png', '.pdf']:
            return JsonResponse({'msg': '文件格式必须为jpg, png, pdf'})
        TaskFile.objects.create(file=f, task=task)

    task.filing = True
    task.save()

    wh = WorkflowHistory(
        workflowactivity=task.workflowactivity,
        state=State.objects.filter(pk=9).first(),
        log_type=WorkflowHistory.COMMENT,
        note='归档：' + filing_note,
        created_by=request.user,
    )
    wh.save(user=request.user)

    return JsonResponse({'msg': 0})
