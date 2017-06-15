# coding:utf8
import urlparse
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from workflow.models import Workflow, WorkflowActivity
from workflow.signals import workflow_transitioned, workflow_stoped
from msg.models import Messages
from celerymail import send_html_mail, send_msg
# Create your models here.


@receiver(workflow_transitioned)
def auto_send_mail(sender, **kwargs):
    """
    如果task有transition动作被执行, 发邮件提醒
    """
    try:
        task = sender.workflowactivity.apply
    except ObjectDoesNotExist:
        return

    transition = sender.transition
    """定义只有合同的申请者,下一个动作的接收者能收到邮件"""
    # transactor = kwargs.get('user')     # 动作执行人
    mail_receivers = set()
    # mail_receivers.add(task.workflowactivity.created_by.email)

    if transition.label == 'leave-start':
        mail_receivers.add(task.workflowactivity.created_by.pro.superior.email)
        accepter = [task.workflowactivity.created_by.pro.superior]
        task.label = 'leave-pro'
    elif transition.label == 'leave-pro1':
        mail_receivers.add(task.workflowactivity.created_by.pro.department.user.email)
        accepter = [task.workflowactivity.created_by.pro.department.user]
        task.label = 'leave-department'
    elif transition.label in ['leave-pro3', 'leave-department3', 'leave-glc3',
                              'leave-pro2', 'leave-department2', 'leave-glc1']:
        if transition.label in ['leave-pro2', 'leave-department2', 'leave-glc1']:
            task.result = 1
            apply_date = datetime.datetime.strftime(task.apply_date, '%Y%m%d')
            holiday_obj = UserHoliday.objects.get(user=task.user)

            monthapply_obj, _ = MonthApply.objects.get_or_create(user=task.user, year_month=apply_date[:6])

            if task.leavetype.name == '加班':
                holiday_obj.overtime_day = holiday_obj.overtime_day + task.total_day
                holiday_obj.save()
            elif task.leavetype.name == '调休':
                holiday_obj.overtime_day = holiday_obj.overtime_day - task.total_day
                holiday_obj.save()
            elif task.leavetype.name == '年假':
                holiday_obj.year_day = holiday_obj.year_day - task.total_day
                holiday_obj.save()
            monthapply_obj.apply_day = monthapply_obj.apply_day + task.total_day
            monthapply_obj.save()
        else:
            task.result = 0
        task.label = ''
        task.status = True
        accepter = 'no_msg'
        mail_receivers.add(task.workflowactivity.created_by.email)
    else:
        task.label = 'leave-glc'
        for u in transition.to_state.users.select_related().all():
            mail_receivers.add(u.email)
        accepter = list(transition.to_state.users.all())
    task.save()
    """参与者邮箱"""

    mail_receivers = filter(lambda x: x, mail_receivers)
    message = '<h3>{title}</h3>' \
              '<a href="{link}">假期类型： {name}</a>' \
              '<p>申请人： {applicant}</p>' \
              '<p>状态描述： {desc}</p>' \
        .format(
            title='CAS - 假期提醒',
            name=task.leavetype.name,
            link=urlparse.urljoin(settings.MAIN_DOMAIN, task.get_absolute_url()),
            applicant=task.workflowactivity.created_by.get_full_name(),
            desc=transition.to_state.description
        )
    send_html_mail('CAS - 假期申请', message, mail_receivers)
    try:
        Messages.objects.get(app='请假', mid=task.pk).delete()
    except Messages.DoesNotExist:
        pass

    if accepter != 'no_msg':
        msg = Messages(subject=task.leavetype.name, description='由 %s 提交的假期申请' % task.workflowactivity.created_by.first_name,
                       app='请假', sender=task.workflowactivity.created_by, mid=task.pk, url='/leave/notes/')
        msg.save(accepter=accepter)

        data = {'agent_id': 0, 'msg_type': 'text', 'remark': 'AlarmId|wer3sadasd28237', 'to_dep': '', 'to_tag': '',
                'to_user': ','.join([obj.first_name for obj in accepter]), 'topic': 'dev_alarm',
                'Content': "<a href='http://cas.100credit.cn/leave/notes/'>请假 %s 由 %s 提交的假期申请</a>" % (task.leavetype.name, task.workflowactivity.created_by.first_name),
                'project_name': 'CAS待办事项'}
        send_msg.delay(data)


class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='类型名称')
    en_name = models.CharField("英文名", default='', max_length=20, blank=True)
    include_day = models.IntegerField(null=True, blank=True, verbose_name='包含几天假期')
    name_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='别名')
        
    class Meta:
        verbose_name = '假期类型'
        verbose_name_plural = '假期类型列表'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Apply(models.Model):
    RESULT_NUM = (
        (0, '拒绝'),
        (1, '同意'),
        (2, '已取消'),
    )
    HALF_NUM = (
        (0, '结束'),
        (1, '开始'),
    )
    workflowactivity = models.OneToOneField(WorkflowActivity, blank=True, null=True)
    label = models.CharField(max_length=64, default='', blank=True)

    user = models.ForeignKey(User, verbose_name='申请人')
    start_date = models.DateField(verbose_name='起始日期')
    end_date = models.DateField(verbose_name='结束日期')
    leavetype = models.ForeignKey(LeaveType, verbose_name='假期类型')
    upfile = models.FileField(max_length=500, upload_to='file/%Y/%m', null=True, blank=True)
    half = models.IntegerField(choices=HALF_NUM, null=True, blank=True, verbose_name='半天是开始日期还是结束日期')
    desc = models.TextField(max_length=1000, null=True, blank=True, verbose_name='申请理由')
    apply_date = models.DateTimeField(auto_now_add=True, verbose_name='申请日期')
    total_day = models.FloatField(null=True, blank=True, verbose_name='合计天数')
    status = models.BooleanField(default=False, verbose_name="审批状态")
    result = models.IntegerField(choices=RESULT_NUM, null=True, blank=True, verbose_name="审批结果")

    class Meta:
        verbose_name = '申请单'
        verbose_name_plural = '申请单列表'
        ordering = ['-apply_date']

    def __unicode__(self):
        return '%s : %s' % (self.user.first_name, self.apply_date)

    def create(self, user):
        workflow = Workflow.objects.filter(name="请假").first()
        if not workflow:
            raise ValueError('没有工作流!')
        workflowactivity = WorkflowActivity(workflow=workflow, created_by=user)
        workflowactivity.save()
        self.workflowactivity = workflowactivity
        self.save()

        workflowactivity.start(user)
        return True

    def get_current_state(self):
        return self.workflowactivity.current_state

    def get_current_transitions(self):
        """当前state支持的transitions"""
        return self.workflowactivity.current_transitions()

    def has_perm_use_transitions(self, user):
        """当前state下, *user*可以使用的transitions"""
        state = self.get_current_state()
        transitions = self.workflowactivity.workflow.transitions.filter(from_state=state) \
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
        return reverse('note_detail', kwargs={'pk': self.pk})


class UserHoliday(models.Model):
    user = models.OneToOneField(User, verbose_name='个人')
    year_day = models.FloatField(default=0, blank=True, verbose_name='年假')
    can_use_day = models.FloatField(default=0, blank=True, verbose_name='可用年假')
    overtime_day = models.FloatField(default=0, blank=True, verbose_name='调休')

    class Meta:
        verbose_name = '个人假期统计'
        verbose_name_plural = '个人假期统计列表'
        ordering = ['-id']
    
    def __unicode__(self):
        return self.user.first_name


class MonthApply(models.Model):
    user = models.ForeignKey(User, verbose_name='个人')
    year_month = models.CharField(max_length=100, null=True, blank=True, verbose_name='当前年月')
    add_day = models.FloatField(default=0, blank=True, verbose_name='非工作日加班')
    apply_day = models.FloatField(default=0, blank=True, verbose_name='本月申请')

    class Meta:
        verbose_name = '月申请记录'
        verbose_name_plural = '月申请记录'
        unique_together = ['user', 'year_month']
        ordering = ['-id']
    
    def __unicode__(self):
        return  '%s : %s'%(self.user.first_name, self.year_month)
