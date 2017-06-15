# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from workflow.signals import (
    workflow_started, workflow_pre_change, workflow_post_change,
    workflow_transitioned, workflow_commented, workflow_ended, workflow_stoped
)
from workflow.exceptions import (
    UnableToStartWorkflow, UnableToProgressWorkflow, UnableToAddCommentToWorkflow
)


class Workflow(models.Model):

    name = models.CharField('名称', max_length=128)
    label = models.CharField('标签', max_length=64)
    description = models.TextField('描述', blank=True, default='')
    created_by = models.ForeignKey(User, verbose_name='创建人')
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['name']
        verbose_name = 'Workflow'
        verbose_name_plural = '工作流类型'
        permissions = (
            ('can_manage_workflows', 'Can manage workflows'),
        )

    def __unicode__(self):
        return self.name


class State(models.Model):
    name = models.CharField('名称', max_length=128)
    label = models.CharField('标签', blank=True, default='', max_length=128)
    description = models.TextField('描述', blank=True, default='')
    is_start_state = models.BooleanField('是起始状态吗?', default=False)
    is_end_state = models.BooleanField('是结束状态吗?', default=False)
    workflow = models.ForeignKey(Workflow, related_name='states')
    # The following two fields define *who* has permission to
    # view the item in this state.
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ['workflow']
        verbose_name = 'State'
        verbose_name_plural = '状态'

    def __unicode__(self):
        return '%s - %s - %s' % (self.name, self.description, self.workflow)

    def can_view_users(self):
        return User.objects.filter(
                    Q(groups__in=self.groups.all()) | Q(id__in=self.users.values_list('id', flat=True))
                ).all().distinct()

    def has_perm_view(self, user):
        return user in self.can_view_users()


class Transition(models.Model):
    name = models.CharField('名称', max_length=128)
    label = models.CharField('label', max_length=24, blank=True, default='')
    description = models.TextField('描述', blank=True, default='')
    workflow = models.ForeignKey(Workflow, related_name='transitions')
    from_state = models.ForeignKey(State, related_name='transitions_from')
    to_state = models.ForeignKey(State, related_name='transitions_into')
    # The following two fields define *who* has permission to
    # use this transition to move between states.
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ['workflow']
        verbose_name = 'Transition'
        verbose_name_plural = '流程'

    def __unicode__(self):
        return self.name

    def can_use_users(self):
        return User.objects.filter(
                    Q(groups__in=self.groups.all()) | Q(id__in=self.users.values_list('id', flat=True))
                ).all().distinct()

    def has_perm_use(self, user):
        return user in self.can_use_users()


class WorkflowActivity(models.Model):
    """
    具体某个工作流的工单实例, 每开启一个工单, 就生成一个WorkflowActivity的实例
    """
    workflow = models.ForeignKey(Workflow)
    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(blank=True, null=True)
    current_state = models.ForeignKey(State, blank=True, null=True)

    class Meta:
        ordering = ['-created_on', '-completed_on']
        verbose_name = 'Workflow Activity'
        verbose_name_plural = '工作流实例'
        permissions = (
            ('can_start_workflow', 'Can start a workflow'),
        )

    def current_transitions(self):
        """
        当前state可执行的transitions, 即当前可执行的操作
        """
        if self.current_state:
            return self.current_state.transitions_from.all()
        else:
            return []

    def start(self, user):
        """
        启动WorkflowActivity, 运行启动的transition, 返回WorkflowHistory实例
        """
        # Validation
        # 1. The workflow activity isn't already started
        if self.current_state:
            raise UnableToStartWorkflow('Already started')
        # 2. The workflow activity hasn't been force_stopped before being started
        if self.completed_on:
            raise UnableToStartWorkflow('Already completed')
        # 3. There is exactly one start state
        start_state = State.objects.filter(workflow=self.workflow, is_start_state=True)
        if start_state.count() != 1:
            raise UnableToStartWorkflow('There are multiple/no start-state')
        # 4. There is exactly one start transition

        transitions = self.workflow.transitions.filter(from_state=start_state)
        if transitions.count() != 1:
            raise UnableToStartWorkflow('There are multiple/no start-transition')

        transition = transitions.first()

        self.add_participant(user)
        if self.workflow == Workflow.objects.filter(name='请假').first():
            self.add_participant(self.created_by.pro.superior)
        else:
            self.add_participant(self.created_by.pro.department.user)

        wh = WorkflowHistory(
                workflowactivity=self,
                state=transition.to_state,
                log_type=WorkflowHistory.TRANSITION,
                transition=transition,
                note='提交合同' if self.workflow == Workflow.objects.filter(name='采购合同').first() else '发起申请',
                created_by=user,
            )
        wh.save(user=user)
        self.current_state = transition.to_state
        self.save()

        return wh

    def progress(self, transition, user, note=''):
        """
        执行一个transition, 创建并返回该WorkflowHistory实例
        """
        if not self.current_state:
            raise UnableToProgressWorkflow('Start the workflow before attempting to transition')
        # 2. Make sure it's parent is the current state
        if transition.from_state != self.current_state:
            raise UnableToProgressWorkflow('Transition not valid (wrong parent)')
        # 3. Make sure *user* has permission to make this *transition*
        if not transition.has_perm_use(user):
            raise UnableToProgressWorkflow('*User* has not permission to use the specified transition')

        self.add_participant(user)

        self.current_state = transition.to_state
        # If we're at the end then mark the workflow activity as completed on today
        if transition.to_state.is_end_state:
            self.completed_on = now()
        self.save()

        if transition.label in ['start', 'th', 'leave-start', 'leave-pro1', 'leave-pro2',
                                'leave-pro3', 'leave-glc1', 'leave-glc3', 'leave-department3']:    # 合同;请假 start with 'leave'
            if transition.label == 'leave-pro1':
                self.add_participant(self.created_by.pro.department.user)
            else:
                pass
        elif transition.label in ['department', ''] and transition.name == '退回':    # 合同
            pass
        else:
            for obj in transition.to_state.users.select_related().all():
                self.add_participant(obj)

        wh = WorkflowHistory(
                workflowactivity=self,
                state=transition.to_state,
                log_type=WorkflowHistory.TRANSITION,
                transition=transition,
                note=note if note else transition.description,
                created_by=user,
            )
        wh.save(user=user)

        return wh

    def add_comment(self, user, note):
        """
        只添加一个WorkflowHistory用于记录信息, 不执行transition
        """
        if not note:
            raise UnableToAddCommentToWorkflow('Cannot add an empty comment(note)')

        wh = WorkflowHistory(
                workflowactivity=self,
                state=self.current_state,
                log_type=WorkflowHistory.COMMENT,
                note=note,
                created_by=user,
            )
        wh.save()
        return wh

    def add_participant(self, user):
        # for user in args:
        participant = Participant(user=user, workflowactivity=self)
        try:
            participant.save()
            return True
        except IntegrityError:
            return False

    def force_stop(self, user, reason):
        # Lets try to create an appropriate entry in the WorkflowHistory tables
        state = State.objects.filter(name='终止').first()

        self.current_state = state
        self.completed_on = now()
        self.save()

        final_step = WorkflowHistory(
                workflowactivity=self,
                state=self.current_state,
                log_type=WorkflowHistory.STOP,
                note=reason,
                created_by=user,
            )
        final_step.save(reason=reason)

        return final_step


class Participant(models.Model):
    """
    任务的参与者
    """

    user = models.ForeignKey(User)
    workflowactivity = models.ForeignKey(WorkflowActivity, related_name='participants')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'
        unique_together = ('user', 'workflowactivity')

    def __unicode__(self):
        return self.user.get_full_name()


class WorkflowHistory(models.Model):

    TRANSITION = 1
    COMMENT = 2
    STOP = 3

    LOG_TYPE_CHOICE = (
        (TRANSITION, 'Transition'),
        (COMMENT, 'Comment'),
    )

    workflowactivity = models.ForeignKey(WorkflowActivity, related_name='history')
    log_type = models.IntegerField(
            choices=LOG_TYPE_CHOICE,
            help_text='The type of thing being logged'
        )
    state = models.ForeignKey(
            State, null=True,
            help_text='The state at this point in the workflow history'
        )
    transition = models.ForeignKey(
            Transition, null=True, related_name='history',
            help_text='The transition relating to this happening in the workflow history'
        )
    note = models.TextField('Note', blank=True, default='')
    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Workflow History'
        verbose_name_plural = '历史记录'

    def __unicode__(self):
        return '%s created by %s' % (self.note, self.created_by.get_full_name())

    def save(self, reason='', user=None, *args, **kwargs):
        workflow_pre_change.send(sender=self)
        super(WorkflowHistory, self).save(*args, **kwargs)
        workflow_post_change.send(sender=self)
        if self.log_type == self.TRANSITION:
            workflow_transitioned.send(sender=self, user=user, reason=self.note)
        elif self.log_type == self.COMMENT:
            workflow_commented.send(sender=self)
        elif self.log_type == self.STOP:
            workflow_stoped.send(sender=self, reason=reason)
        if self.state:
            if self.state.is_start_state:
                workflow_started.send(sender=self.workflowactivity)
            elif self.state.is_end_state:
                workflow_ended.send(sender=self.workflowactivity)


class WorkflowObjectRelation(models.Model):

    content_type = models.ForeignKey(ContentType, related_name='workflow_object')
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='content_id')
    workflow = models.ForeignKey(Workflow, verbose_name='Workflow')

    class Meta:
        unique_together = ('content_type', 'content_id')
        verbose_name = 'Workflow object relation'
        verbose_name_plural = 'Workflow object relations'

    def __unicode__(self):
        return '%s %s - %s' % (self.content_type, self.content_id, self.workflow.name)
