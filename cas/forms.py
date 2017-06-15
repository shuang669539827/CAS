#coding:utf8
import datetime

from django import forms

from models import Pro, Project, Department, UserRole, Zone, ProjectRole


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, label='用户名')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')
    repassword = forms.CharField(widget=forms.PasswordInput, label='密码确认')


class InfoForm(forms.Form):
    SEX_NUM = (
        (0, '男'),
        (1, '女'),
        )
    FLOOR_NUM = (
        (1, '2F'),
        (2, '20F'),
        (3, '石景山')
    )
    name = forms.CharField(required=True, max_length=100, label='姓名')
    num_id = forms.CharField(required=True, max_length=100, label='员工编号')
    sex = forms.IntegerField(required=True, widget=forms.Select(choices=SEX_NUM), label='性别')
    floor = forms.IntegerField(required=True, widget=forms.Select(choices=FLOOR_NUM), label='楼层')
    department = forms.ModelChoiceField(required=True, queryset=Department.objects.all(), label='部门')
    superior_email = forms.EmailField(required=True, label='上级邮箱')
    work_year = forms.IntegerField(required=True, initial=1, label='工龄(年/正整数)')
    in_time = forms.DateField(required=True, initial=datetime.datetime.now().date, label='入职时间（格式：YYYY-MM-dd）')
    email = forms.EmailField(required=True, label='百融个人邮箱(未开通也要填写)')
    role = forms.ModelChoiceField(required=False, queryset=UserRole.objects.all(), label="部门角色")
    zone = forms.ModelChoiceField(required=False, initial=Zone.objects.get(name_id=1), queryset=Zone.objects.all(), label="区域")
    id_num = forms.CharField(required=False, max_length=100, label='身份证号')
    qq = forms.CharField(required=False, max_length=100, label="qq")
    phone = forms.CharField(required=False, max_length=200, label="联系电话")
    birth = forms.CharField(required=False, label='生日')
    birthadd = forms.CharField(required=False, max_length=100, label='籍贯')


class RoleForm(forms.Form):
    project = forms.CharField(required=True, max_length=200, label='项目名称', widget=forms.TextInput(attrs={'readonly': 'true'}))
    first_name = forms.CharField(required=True, max_length=200, label='姓名')
    projectrole = forms.CharField(required=True, max_length=200, label='项目角色')


class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectRole
        fields = ['name']


class DisRoleForm(forms.Form):
    project = forms.ModelChoiceField(required=True, queryset=Project.objects.all(), label='项目名称', widget=forms.TextInput(attrs={'readonly': 'true'}))
    first_name = forms.CharField(required=True, max_length=200, label='姓名', widget=forms.TextInput(attrs={'readonly': 'true'}))
    projectrole = forms.CharField(required=True, max_length=200, label='项目角色')


class ProForm(forms.ModelForm):

    class Meta:
        model = Pro
        exclude = ['user', 'vercode', 'superior', 'permission', 'add_role_perm', 'vacation_manager', 'dinner_manager', 'user_manger', 'apply_subject_perm']
    superior = forms.CharField(widget=forms.TextInput, label='上级邮箱')
    status = forms.BooleanField(widget=forms.CheckboxInput, label='在职状态', required=False)


class MyForm(forms.ModelForm):
    class Meta:
        model = Pro
        fields = ['sex', 'floor', 'id_num', 'qq', 'phone', 'birth', 'birthadd']        


class PasswdForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label='新密码')
    password2 = forms.CharField(widget=forms.PasswordInput, label='确认密码') 


class ApplyPermForm(forms.Form):
    project = forms.ModelChoiceField(required=True, queryset=None, label='项目名称')
    role = forms.ModelChoiceField(required=True, initial=ProjectRole.objects.get(name_id=1), queryset=ProjectRole.objects.all(), label='项目角色')
    zone = forms.ModelChoiceField(required=True, initial=Zone.objects.get(name_id=1), queryset=Zone.objects.all(), label='大区')

    def __init__(self, dptId, *args, **kwargs):

        super(ApplyPermForm, self).__init__(*args, **kwargs)
        try:
            department = Department.objects.get(pk=dptId)
            self.fields['project'].queryset = department.permission
        except Department.DoesNotExist:
            pass


class ApplyPermFormPost(forms.Form):
    project = forms.ModelChoiceField(required=True, queryset=Project.objects.all(), label='项目名称')
    role = forms.ModelChoiceField(required=True, initial=ProjectRole.objects.get(name_id=1), queryset=ProjectRole.objects.all(), label='项目角色')
    zone = forms.ModelChoiceField(required=True, initial=Zone.objects.get(name_id=1), queryset=Zone.objects.all(), label='大区')