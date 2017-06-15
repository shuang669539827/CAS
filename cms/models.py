# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import urlparse
import os

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from celerymail import send_html_mail, send_msg
from workflow.models import Workflow, WorkflowActivity, WorkflowHistory, Participant, State
from workflow.signals import workflow_transitioned, workflow_stoped
from msg.models import Messages


logger = logging.getLogger('daserr')


@receiver(workflow_transitioned)
def auto_send_mail(sender, **kwargs):
    """
    如果task有transition动作被执行, 发邮件提醒
    """
    try:
        task = sender.workflowactivity.task
    except ObjectDoesNotExist:        # catch RelatedObjectDoesNotExist
        return

    transition = sender.transition

    """定义只有合同的申请者,动作执行人,下一个动作的接收者能收到邮件"""
    transactor = kwargs.get('user')     # 动作执行人
    reason = kwargs.get('reason')
    mail_receivers = set()
    mail_receivers.add(task.workflowactivity.created_by.email)
    mail_receivers.add(transactor.email)

    if transition.label == 'start':
        mail_receivers.add(task.workflowactivity.created_by.pro.department.user.email)
        task.label = 'department'
    elif transition.label in ['department', ''] and transition.name == '退回':
        task.label = 'start'
    else:
        for u in transition.to_state.users.select_related().all():
            mail_receivers.add(u.email)
        task.label = '' if transition.name != '退回' else 'start'
    task.save()

    """参与者邮箱"""

    mail_receivers = filter(lambda x: x, mail_receivers)

    if transition.name == '退回':
        message = '<h3>{title}</h3>' \
                  '<a href="{link}">合同名称： {name}</a>' \
                  '<p>申请人： {applicant}</p>' \
                  '<p>当前状态： {state}</p>'\
                  '<p>描述： {desc}</p>' \
                  '<p>原因： {reason}</p>' \
            .format(
                title='CAS - 合同提醒',
                name=task.name,
                link=urlparse.urljoin(settings.MAIN_DOMAIN, task.get_absolute_url()),
                applicant=task.workflowactivity.created_by.get_full_name(),
                state=transition.to_state.description,
                desc=task.note,
                reason=reason
            )
    else:
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
                state=transition.to_state.description,
                desc=task.note
            )
    send_html_mail('CAS - 合同提醒', message, mail_receivers)
    try:
        Messages.objects.get(app='采购合同审批', mid=task.pk).delete()
    except Messages.DoesNotExist:
        pass

    if transition.label == 'start':
        accepter = [task.workflowactivity.created_by.pro.department.user]
    elif transition.name == '退回':
        accepter = [task.workflowactivity.created_by]
    else:
        accepter = list(transition.to_state.users.all())
    msg = Messages(subject=task.name, description='由 %s 提交的合同' % task.workflowactivity.created_by.first_name,
                   app='采购合同审批', sender=task.workflowactivity.created_by, mid=task.pk, url='/cms/list/')
    msg.save(accepter=accepter)

    data = {'agent_id': 0, 'msg_type': 'text', 'remark': 'AlarmId|wer3sadasd28237', 'to_dep': '', 'to_tag': '',
            'to_user': ','.join([obj.first_name for obj in accepter]), 'topic': 'dev_alarm',
            'Content': "<a href='http://cas.100credit.cn/leave/notes/'>采购合同审批  %s  由 %s 提交的合同</a>" % (task.name, task.workflowactivity.created_by.first_name),
            'project_name': 'CAS待办事项'}
    send_msg.delay(data)


@receiver(workflow_stoped)
def send_stop_mail(sender, **kwargs):
    """
    如果task有stop动作被执行, 发邮件提醒
    """
    reason = kwargs.get('reason')
    try:
        task = sender.workflowactivity.task
    except ObjectDoesNotExist:
        return
    task.label = 'end'
    task.save()
    participants = sender.workflowactivity.participants.all()

    mail_receivers = set()
    mail_receivers.add(sender.created_by.email)
    for p in participants:
        mail_receivers.add(p.user.email)

    mail_receivers = filter(lambda x: x, mail_receivers)

    message = '<h3>{title}</h3>' \
              '<a href="{link}">合同名称： {name}</a>' \
              '<p>申请人： {applicant}</p>' \
              '<p>当前状态： {state}</p>' \
              '<p>描述： {desc}</p>' \
              '<p>原因： {reason}</p>' \
        .format(
            title='CAS - 合同提醒',
            name=task.name,
            link=urlparse.urljoin(settings.MAIN_DOMAIN, task.get_absolute_url()),
            applicant=task.workflowactivity.created_by.get_full_name(),
            state=sender.workflowactivity.current_state.description,
            desc=task.note,
            reason=reason
        )
    send_html_mail('CAS - 合同提醒', message, mail_receivers)

    Messages.objects.get(app='采购合同审批', mid=task.pk).delete()


class Partyfirst(models.Model):
    name = models.CharField(max_length=255, verbose_name='名称', unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '甲方'
        verbose_name_plural = '甲方'

    def __unicode__(self):
        return self.name


class Partysecond(models.Model):
    name = models.CharField(max_length=255, verbose_name='名称', unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '乙方'
        verbose_name_plural = '乙方'

    def __unicode__(self):
        return self.name


class Task(models.Model):
    workflowactivity = models.OneToOneField(WorkflowActivity, blank=True, null=True)

    label = models.CharField(max_length=125, default='', blank=True, verbose_name='传输状态')
    partyf = models.ForeignKey(Partyfirst, null=True, blank=True, verbose_name='甲方', related_name='partyf')
    partys = models.ForeignKey(Partysecond, null=True, blank=True, verbose_name='乙方', related_name='partys')
    name = models.CharField(max_length=256, verbose_name='名称')
    univalent = models.FloatField(blank=True, null=True, verbose_name='单价')
    total = models.FloatField(blank=True, null=True, verbose_name='总价')
    note = models.TextField(blank=True, default='', verbose_name='说明')

    create_by = models.ForeignKey(User, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    filing = models.BooleanField("归档状态", default=False, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '任务'
        verbose_name_plural = '任务列表'
        permissions = (
            ('assign_te', 'Can assign TE'),
            ('progress_transition', 'Make a transition'),
            ('place', 'Contract filing'),
            ('watch', 'Can see all contract')
        )

    def create(self, user):
        workflow = Workflow.objects.filter(name="采购合同").first()
        if not workflow:
            raise ValueError('没有工作流!')
        workflowactivity = WorkflowActivity(workflow=workflow, created_by=user)
        workflowactivity.save()
        self.workflowactivity = workflowactivity
        self.save()

        workflowactivity.start(user)
        return True

    def get_current_state(self):
        if self.workflowactivity:
            return self.workflowactivity.current_state
        else:
            return 'no workflow'

    def get_participants(self):
        return self.workflowactivity.participant.user.all()

    def get_current_transitions(self):
        """当前state支持的transitions"""
        return self.workflowactivity.current_transitions()

    def has_perm_use_transitions(self, user):
        """当前state下, *user*可以使用的transitions"""
        state = self.get_current_state()
        transitions = self.workflowactivity.workflow.transitions.filter(from_state=state)\
            .filter(Q(users=user) | Q(groups__in=user.groups.all())).all()
        return transitions

    def has_perm_view(self, user):
        """判断*user*是否可以看到此task"""
        if self.workflowactivity.participants.filter(user=user).exists():
            return True
        current_state = self.get_current_state()
        if current_state:
            if current_state.has_perm_view(user):
                return True

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('task_delete', kwargs={'pk': self.pk})


class TaskFile(models.Model):
    task = models.ForeignKey(Task, related_name='attachment')
    file = models.FileField(upload_to='task/%Y/%m')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '任务'
        verbose_name_plural = '任务附件'

    def __unicode__(self):
        return '%s' % os.path.basename(self.file.name)

    def get_absolute_url(self):
        return reverse('down_file', kwargs={'pk': self.id})
