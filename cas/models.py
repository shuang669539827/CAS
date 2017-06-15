# coding:utf8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class News(models.Model):
    name = models.CharField(max_length=100, verbose_name='新闻')

    class Meta:
        verbose_name = '新闻列表'
        verbose_name_plural = '新闻列表'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100, verbose_name='导航')
    url = models.CharField(max_length=100, verbose_name='描述')

    class Meta:
        verbose_name = '导航菜单'
        verbose_name_plural = '导航菜单'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class UserRole(models.Model):
    name = models.CharField(max_length=60, verbose_name='角色', unique=True)
    name_id = models.IntegerField(unique = True, null=True, blank=True, verbose_name='双索引')

    class Meta:
        verbose_name = '人物角色'
        verbose_name_plural = '人物角色'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class ProjectRole(models.Model):
    name = models.CharField(max_length=60, verbose_name='项目角色', unique=True)
    name_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='双索引')

    class Meta:
        verbose_name = '项目角色'
        verbose_name_plural = '项目角色'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=128, verbose_name='项目名称', unique=True)
    url = models.CharField(max_length=128, verbose_name='项目地址', unique=True)
    user = models.ForeignKey(User, verbose_name='项目维护人', null=True, blank=True)
    desc = models.CharField(max_length=128, verbose_name='项目描述')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = "项目列表"
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=60, verbose_name='部门', unique=True)
    user = models.ForeignKey(User, related_name='leader', verbose_name='部门领导人', null=True, blank=True)
    name_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='双索引')
    permission = models.ManyToManyField(Project, blank=True, verbose_name="访问项目权限")
    bp = models.ForeignKey(User, related_name='bp', verbose_name='人事负责人', null=True, blank=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门列表'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField(max_length=60, verbose_name='区域名字', unique=True)
    name_id = models.IntegerField(unique = True, null=True, blank=True, verbose_name='双索引')

    class Meta:
        verbose_name = "区域"
        verbose_name_plural = "区域列表"
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Pro(models.Model):
    SEX_NUM = (
        (0, '男'),
        (1, '女'),
        )
    FLOOR_NUM = (
        (1, '2F'),
        (2, '20F'),
        (3, '石景山')
    )
    user = models.OneToOneField(User, verbose_name='用户')
    num_id = models.CharField(max_length=100, default='', blank=True, verbose_name='员工编号')
    sex = models.IntegerField(choices=SEX_NUM, default=0, verbose_name='性别')
    floor = models.IntegerField(choices=FLOOR_NUM, default=1, verbose_name='楼层')
    department = models.ForeignKey(Department, null=True, blank=True, verbose_name='部门')
    role = models.ForeignKey(UserRole, null=True, blank=True, verbose_name="职位")
    superior = models.ForeignKey(User, related_name='super', null=True, blank=True, verbose_name='上级')
    zone = models.ForeignKey(Zone, null=True, blank=True, verbose_name="区域")
    work_year = models.IntegerField(default=0, blank=True, verbose_name='工龄(年)')
    id_num = models.CharField(max_length=100, default='', blank=True, verbose_name='身份证号')
    birth = models.CharField(max_length=100, default='', blank=True,verbose_name='生日')
    birthadd = models.CharField(max_length=100, default='', blank=True, verbose_name='籍贯')
    in_time = models.DateField(null=True, blank=True, verbose_name='入职时间')
    qq = models.CharField(max_length=100, blank=True, default='', verbose_name="QQ")
    phone = models.CharField(max_length=200, default='', blank=True, verbose_name="联系电话")
    vercode = models.CharField(max_length=200, default='', blank=True, verbose_name="验证码")
    permission = models.ManyToManyField(Project, blank=True, verbose_name="访问项目权限")
    add_role_perm = models.BooleanField(default=False, verbose_name="项目角色权限")
    vacation_manager = models.BooleanField(default=False, verbose_name="假期管理权限")
    dinner_manager = models.BooleanField(default=False, verbose_name="订餐管理权限")
    user_manger = models.BooleanField(default=False, verbose_name='CAS用户管理')
    apply_subject_perm = models.BooleanField(default=False, verbose_name='CAS审批项目申请权限')
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户列表"
        ordering = ['-id']

    def __unicode__(self):
        return '%s' % self.user.username

    def can_place(self):
        return self.user.has_perm('cms.place')

    def can_watch(self):
        return self.user.has_perm('cms.watch')


class UserProject(models.Model):
    user = models.ForeignKey(User, verbose_name="用户")
    project = models.ForeignKey(Project, verbose_name="项目")
    projectrole = models.ManyToManyField(ProjectRole, blank=True, verbose_name="角色")
    name_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='双索引')

    class Meta:
        verbose_name = '项目角色关系'
        verbose_name_plural = "项目角色关系列表"
        ordering = ['-id']

    def __unicode__(self):
        return self.user.first_name


class ApplyPerm(models.Model):
    RESULT_NUM = (
        (0, '拒绝'),
        (1, '同意'),
        )
    user = models.CharField(max_length=200, default='', blank=True, verbose_name="用户")
    project = models.CharField(max_length=200, default='', blank=True, verbose_name="项目")
    zone = models.CharField(max_length=200, default='', blank=True, verbose_name="大区")
    role = models.CharField(max_length=200, default='', blank=True, verbose_name="角色")
    create_time = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    result = models.IntegerField(choices=RESULT_NUM, null=True, blank=True, verbose_name="审批结果")

    class Meta:
        verbose_name = '权限申请'
        verbose_name_plural = "权限申请列表"
        ordering = ['-id']

    def __unicode__(self):
        return self.user


class ServiceTicket(models.Model):
    user = models.ForeignKey(User, related_name='ticket_user')
    service = models.URLField()
    ticket = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s (%s) - %s" % (self.user.username, self.service, self.created)


class OutAlarm(models.Model):
    mail = models.TextField(verbose_name="离职发送邮件")


