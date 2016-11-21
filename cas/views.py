#coding:utf8
from __future__ import unicode_literals, division
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse, StreamingHttpResponse
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.paginator import Paginator
from django.views.decorators.csrf import  csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage

from email.mime.text import MIMEText
from email.header import Header

from leave.models import UserHoliday, MonthApply
from .forms import InfoForm, PasswdForm, ApplyPermForm\
, ProForm, MyForm, RoleForm, DisRoleForm, ProjectRoleForm
from .models import ServiceTicket, Pro, Project, UserProject, ProjectRole, News, Menu, ApplyPerm, Zone
from .utils import create_service_ticket

import os
import traceback
import smtplib
import re
import random
import time
import datetime
import django
import logging



errlog = logging.getLogger('daserr')


@login_required
def index(request):
    user = request.user
    permissions = user.pro.permission.all()
    projects = Project.objects.all()
    news = News.objects.all()
    menu = Menu.objects.all()
    return render(request, 'index.html'\
        , {"user": user, "projects": projects, "permissions": permissions\
        , "news": news, "menu": menu})


@login_required
def docs(request):
    filename = request.GET.get('filename')
    basedir = os.getcwd() + '/static/pdf/'+ filename
    def file_iterator(file_name, chunk_size=512):
        with open(basedir) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    response = StreamingHttpResponse(file_iterator(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
    return response


class LoginView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        service = request.GET.get('service')
        if request.user.is_authenticated():
            user_id = request.user.id
            user_obj = User.objects.get(pk=user_id)
            if service:
                ticket = create_service_ticket(user_obj, service)
                return redirect(service + '/?ticket=' + ticket)
            else:
                return HttpResponseRedirect('/index/')
        elif service:
            if request.user.is_authenticated():
                ticket = create_service_ticket(request.user, service)
                return HttpResponseRedirect(service + '/?ticket=' + ticket)
            else:
                return render(request, 'login.html', {'service': service})
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('Username')
        password = request.POST.get('Password')
        service = request.POST.get('service')
        user = authenticate(username=username, password=password)
        error = ''
        if user is not None:
            if user.is_active:
                if service:
                    ticket = create_service_ticket(user, service)
                    return redirect(service + '/?ticket=' + ticket)
                else:
                    auth_login(request, user)
                    return HttpResponseRedirect('/')
            else:
                error = '账户被冻结'
        else:
            error = '用户名或密码错误'
        return render(request, 'login.html', {"error": error, "service": service})


def validate(request):
    ticket = request.GET.get('ticket')
    if ticket is not None:
        try:
            ticket_obj = ServiceTicket.objects.get(ticket=ticket)
            user = ticket_obj.user
            service = ticket_obj.service
            project = Project.objects.get(url=service)
            try:
                userproject = UserProject.objects.get(user=user,project=project)
                role = userproject.projectrole.all()[0]
            except Exception:
                role = ProjectRole.objects.get(name_id=1)
            ticket_obj.delete()
            return JsonResponse({'status':'success', 'email':user.email, 'name':user.first_name\
                , 'user_id':user.id, 'username':user.username, 'pro_id':user.pro.id, 'zone':user.pro.zone.name\
                , 'zone_id':user.pro.zone.id, 'role':role.name, 'role_id':role.id})
        except ServiceTicket.DoesNotExist:
            return JsonResponse({'status':'faile', 'msg':'ticket is out date'})
    return JsonResponse({'status':'faile', 'msg':'no ticket'})
    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def proinfo(request):
    '''成员信息'''
    '''在html中判断一下人物的部门,吧任务传给模板,如果是HR给开账号和,入驻员工信息的权限.'''
    user = request.user
    return render(request, 'proinfo.html', {'user':user})


@login_required
def enterinfo(request):
    '''入驻成员信息'''
    if request.user.pro.user_manger:
        form = InfoForm()
        user = request.user
        if request.method == 'POST':
            form = InfoForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                name = form.cleaned_data['name']
                num_id = form.cleaned_data['num_id']
                sex = form.cleaned_data['sex']
                floor = form.cleaned_data['floor']
                department = form.cleaned_data['department']
                superior_email = form.cleaned_data['superior_email']
                role = form.cleaned_data['role']
                in_time = form.cleaned_data['in_time']
                zone = form.cleaned_data['zone']
                id_num = form.cleaned_data['id_num']
                qq = form.cleaned_data['qq']
                phone = form.cleaned_data['phone']
                birth = form.cleaned_data['birth']
                birthadd = form.cleaned_data['birthadd']
                work_year = form.cleaned_data['work_year']
                try:
                    superior = User.objects.get(email=superior_email)
                except User.DoesNotExist:
                    return render(request, 'enterinfo.html', {'form': form, "error":"上级邮箱有误！", 'user':user})
                if email.split('@')[1] == '100credit.com':
                    username = email.split('@')[0]
                    password = make_password('123', None, 'pbkdf2_sha256')
                    try:
                        user = User.objects.create(username=username, password=password\
                            , first_name=name, email=email)
                        Pro.objects.create(user=user, sex=sex, id_num=id_num, birth=birth, num_id=num_id\
                            , birthadd=birthadd, floor=floor, department=department, superior=superior\
                            , zone=zone, role=role, work_year=work_year, qq=qq, phone=phone, in_time=in_time)
                    except Exception:
                        errlog.error('存储用户错误:' + traceback.format_exc())
                        error = '该邮箱已注册'
                        return render(request, 'enterinfo.html', {'form': form, "error":error, 'user':user})
                    content = "你已开通CAS账号，用户名:%s，密码:123,登陆地址:cas.100credit.cn"%(str(username))
                else:
                    return render(request, 'enterinfo.html', {'form': form, "error":"非百融邮箱", 'user':user})
                today = 365 - time.localtime().tm_yday
                if work_year < 1:
                    year_day = 0
                elif work_year < 10:
                    year_day = round((today/365)*5)
                elif work_year < 20:
                    year_day = round((today/365)*10)
                else:
                    year_day = round((today/365)*15)
                UserHoliday.objects.create(user=user, year_day=year_day)
                year = datetime.datetime.now().year
                month = datetime.datetime.now().month
                if month < 10:
                    year_month = str(year) + '0' + str(month)
                else:
                    year_month = str(year) + str(month)
                MonthApply.objects.create(user=user, year_month=year_month)
                try:
                    send_mail([email], 'CAS系统账号开通', content)
                except smtplib.SMTPRecipientsRefused:
                    content = '%s的邮箱还未开通'%(str(username))
                    send_mail(['cas@100credit.com'], 'CAS系统账号开通', content)   #添加人事邮箱
                return HttpResponseRedirect('/prolist/')
            else:
                form = InfoForm()
                return render(request, 'enterinfo.html', {'form': form, 'error': '日期格式有误！', 'user':user})

        return render(request, 'enterinfo.html', {'form': form, 'user':user})
    else:
        raise Http404


@login_required
def prosearch(request):
    '''搜索用户'''
    if request.user.pro.user_manger:
        name = request.POST.get('search')
        if not name:
            return HttpResponseRedirect('/prolist/')
        num_page = User.objects.filter(first_name__icontains=name)
        user = request.user
        return render(request, 'prolist.html', {'num_page': num_page, 'user':user, 'name':name})
    else:
        raise Http404


@login_required
def prolist(request):
    '''成员列表'''
    if request.user.pro.user_manger:
        page_num = request.GET.get('page_num')
        userobjs = User.objects.exclude(username='admin')
        p = Paginator(userobjs, 15)
        user = request.user
        try:
            num_page = p.page(int(page_num))
        except:
            num_page = p.page(1)
        user = request.user
        return render(request, 'prolist.html', {'num_page':num_page, 'user':user})
    else:
        raise Http404


class Alterpro(View):
    '''修改成员信息'''
    def get(self, request):
        if request.user.pro.user_manger:
            user = request.user
            pro_id = request.GET.get('pro_id')
            if pro_id:
                pro = Pro.objects.get(pk=pro_id)
                form = ProForm(instance=pro, initial={'superior': pro.superior.email})
                projects = Project.objects.all()
                return render(request, 'alterpro.html', {'form': form, 'pro_id': pro_id, 'projects': projects, 'user':user, 'pro': pro})
        else:
            raise Http404
    
    def post(self, request):
        if request.user.pro.user_manger:
            user = request.user
            pro_id = request.POST.get('pro_id')
            pro = Pro.objects.get(pk=pro_id)
            sender_to = pro.user.email
            form = ProForm(request.POST, instance=pro)
            projects = Project.objects.all()
            if form.is_valid():
                superior_email = form.cleaned_data['superior']
                try:
                    superior = User.objects.get(email=superior_email)
                except :
                    error = '上级邮箱有误'
                    return render(request, 'alterpro.html', {'form': form, 'pro_id': pro_id, 'projects': projects, 'user':user, 'error':error})
                pro.superior = superior
                pro.save()
                content = '您好，您的用户信息已被修改，详情请登陆cas.100credit.cn个人信息页面查看，如有问题请联系%s : %s'%(user.first_name, user.email)
                try:
                    send_mail([sender_to], 'CAS系统修改用户信息', content)
                except Exception:
                    errlog.error(traceback.format_exc())
                form.save()
                return HttpResponseRedirect('/prolist/')

            return render(request, 'alterpro.html', {'form': form, 'pro_id': pro_id, 'projects': projects, 'user':user})
        else:
            raise Http404


@login_required
def repasswd(request):
    '''修改密码'''
    pro = request.user.pro
    form = PasswdForm()
    if request.method == 'POST':
        user = request.user
        form = PasswdForm(request.POST)
        if form.is_valid():
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                return render(request, 'repasswd.html', {'error': '两次密码输入不一致', 'form': form, 'pro': pro})
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect('/proinfo/')
    return render(request, 'repasswd.html', {'form': form, 'pro':pro})


@login_required
def alterinfo(request):
    pro = request.user.pro
    form = MyForm(instance=pro)
    if request.method == 'POST':
        form = MyForm(request.POST, instance=pro)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/proinfo/')
    return render(request, 'alterinfo.html', {'form': form})


@login_required
def userprojectlist(request):
    page_num = request.GET.get('page_num')
    user = request.user
    projects = Project.objects.filter(user=user)
    objs = UserProject.objects.filter(project__in=projects)
    p = Paginator(objs, 15) 
    try:
        num_page = p.page(int(page_num))
    except:
        num_page = p.page(1)
    user = request.user
    return render(request, 'userprojectlist.html', {'user': user, 'num_page': num_page})


@login_required
def userprojectsearch(request):
    name = request.POST.get('search')
    try:
        searchuser = User.objects.get(first_name=name)
    except User.DoesNotExist:
        errlog.error('正常输出,没有找到该用户')
        return HttpResponseRedirect('/userprojectlist/')
    user = request.user
    projects = Project.objects.filter(user=user)
    num_page = UserProject.objects.filter(project__in=projects, user=searchuser)
    return render(request, 'userprojectlist.html', {'num_page': num_page, 'user':user, 'name': name})


@login_required
def userprojectalter(request):
    if request.method == 'GET':
        obj_id = request.GET.get("obj_id")
        obj = UserProject.objects.get(pk=obj_id)
        project = obj.project.name
        first_name = obj.user.first_name
        projectroles = obj.projectrole.all()
        char = ','.join([projectrole.name for projectrole in projectroles])
        initial = {"project": project, "first_name": first_name, "projectrole": char}
        form = DisRoleForm(initial=initial)
        return render(request, 'alterrole.html', {'form': form, 'obj_id': obj_id})
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            obj_id = request.POST.get("obj_id")
            obj = UserProject.objects.get(pk=obj_id)
            projectrole = form.cleaned_data["projectrole"].split(',')
            try:
                projectroles = ProjectRole.objects.filter(name__in=projectrole)
            except ProjectRole.DoesNotExist:
                error = '有不存在的角色'
                return render(request, 'addrole.html', {'form': form, 'error': error, 'obj_id': obj_id})
            obj.projectrole = projectroles
            obj.save()
            return HttpResponseRedirect('/userprojectlist/')
        errlog.error('修改项目角色，表单提交有误：' + form.errors.as_json())
        return render(request, 'addrole.html', {'form': form, 'obj_id': obj_id})
    

@login_required
def addrole(request):
    user = request.user
    project = Project.objects.get(user=user)
    form = RoleForm(initial={'project': project.name})
    projectroles = ProjectRole.objects.all()
    name_str = ''
    for r in projectroles:
        name_str = name_str + r.name + ','
    name_str = name_str.strip(',')
    if request.method == 'POST':
        projectroles = ProjectRole.objects.all()
        name_str = ''
        for r in projectroles:
            name_str = name_str + r.name + ','
        name_str = name_str.strip(',')
        form = RoleForm(request.POST)
        if form.is_valid():
            pro = form.cleaned_data["project"]
            project = Project.objects.get(name=pro)
            first_name = form.cleaned_data["first_name"]
            projectrole = form.cleaned_data["projectrole"]
            try:
                user = User.objects.get(first_name=first_name)
            except User.DoesNotExist:
                error = '没有该姓名的用户'
                return render(request, 'addrole.html', {'form': form, 'error': error, 'roles': name_str})
            try:
                obj = ProjectRole.objects.get(name=projectrole)
            except ProjectRole.DoesNotExist:
                error = '没有该角色'
                return render(request, 'addrole.html', {'form': form, 'error': error, 'roles': name_str})
            try:
                userproject = UserProject.objects.get(user=user, project=project)
            except UserProject.DoesNotExist:
                userproject = UserProject.objects.create(user=user, project=project)
            userproject.projectrole.add(obj)
            userproject.save()
            return HttpResponseRedirect('/userprojectlist/')
    return render(request, 'addrole.html', {'form': form, 'roles': name_str})


@login_required
def addprojectrole(request):
    form = ProjectRoleForm()
    if request.method == 'POST':
        form = ProjectRoleForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/userproject/add/')
        else:
            form = ProjectRoleForm()
            return render(request, 'addprojectrole.html', {'form': form, 'error': '已有该角色'})
    return render(request, 'addprojectrole.html', {'form': form})


@login_required
def userprojectdel(request):
    obj_id = request.GET.get('obj_id')
    try:
        UserProject.objects.get(pk=obj_id).delete()
    except Exception, e:
        errlog.error('删除用户角色有误：' + traceback.format_exc())
        return JsonResponse({'code': 0})
    return JsonResponse({'code': 1})


@login_required
def applyperm(request):
    form = ApplyPermForm()
    user = request.user
    if request.method == 'POST':
        user = request.user
        form = ApplyPermForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data["project"]
            role = form.cleaned_data["role"]
            zone = form.cleaned_data["zone"]
            ApplyPerm.objects.create(user=user.username, project=project.name, role=role.name, zone=zone.name)
            content = """
                    <p>申请人：%s</p>
                    <p>申请项目：%s</p>
                    <p>申请角色：%s</p>
                    <p>区域：%s</p>
                    <p><a href="http://cas.100credit.cn/">CAS系统</a></p>
                    """%(user.first_name, str(project.name), str(role.name), str(zone.name))
            send_mail(['cas1@100credit.com', user.pro.superior.email], 'CAS系统项目权限申请', content)
            return HttpResponseRedirect("/proinfo/")
    return render(request, "applyperm.html", {'form': form, 'user': user})


@login_required
def applypermlist(request):
    objs = ApplyPerm.objects.filter(status=False)
    user = request.user
    return render(request, "applypermlist.html", {'user': user, 'objs': objs})


@login_required
def applypermres(request):
    apply_id = int(request.GET.get('apply_id'))
    res_num = int(request.GET.get('res_num'))
    if apply_id:
        applyperm_obj = ApplyPerm.objects.get(id=apply_id)
        project = Project.objects.get(name=applyperm_obj.project)
        projectrole = ProjectRole.objects.get(name=applyperm_obj.role)
        zone = Zone.objects.get(name=applyperm_obj.zone)
        user = User.objects.get(username = applyperm_obj.user)
        if res_num == 0:
            applyperm_obj.status = True
            applyperm_obj.result = 0
            applyperm_obj.save()
            content = '您申请的%s:%s，权限已被拒绝。'%(applyperm_obj.project, applyperm_obj.role)
        if res_num == 1:
            applyperm_obj.status = True
            applyperm_obj.result = 1
            applyperm_obj.save()
            try:
                obj = UserProject.objects.get(user=user, project=project)
            except:
                UserProject.objects.create(user=user, project=project)
                obj = UserProject.objects.get(user=user, project=project)
            obj.projectrole.add(projectrole)
            user.pro.permission.add(project)
            user.pro.zone=zone
            user.pro.save()
            content = '您申请的%s:%s，权限已经过审批，请登陆<a href="http://cas.100credit.cn/"">CAS系统</a>查看。'%(applyperm_obj.project, applyperm_obj.role)
        send_mail([user.email], 'CAS系统项目权限申请', content)
    return HttpResponseRedirect('/applypermlist/')


def get_vercode(request):
    email = request.POST.get('email')
    if not email:
        return render(request, "re_passwd.html", {'error': '请输入邮箱'})
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is None:
        return render(request, "re_passwd.html", {'error': '邮箱格式错误'})
    try:
        user = User.objects.get(email=email)
        name = user.first_name
    except User.DoesNotExist:
        return render(request, "re_passwd.html", {'error': '没有和该邮箱匹配的用户'})
    code = random.randint(1000, 9999)
    vercode = str(code) + (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime('%Y%m%d%H%M%S')
    user.pro.vercode = vercode
    user.pro.save()
    content = '您好，' + name + ' ,您的验证码为：' + str(code) + '。您正在申请重置您的CAS系统账号密码，如非本人操作，请忽视！'
    try:
        send_mail([email], 'CAS系统修改密码', content)
    except smtplib.SMTPRecipientsRefused:
        return render(request, "re_passwd.html", {'error': '该邮箱暂未开通'})
    return render(request, 're_passwd.html', {'error': '获取成功', 'param':email})


def re_passwd(request):
    if request.method == 'POST':
        email = request.POST.get('param')
        vercode = request.POST.get('vercode')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        try:
            user = User.objects.get(email=email)
        except user.DoesNotExist:
            return render(request, "re_passwd.html", {'error': '该用户已不存在', 'param':email})
        pro = user.pro
        code = str(pro.vercode)[:4]
        code_time = datetime.datetime.strptime(str(pro.vercode)[4:], "%Y%m%d%H%M%S")
        now = datetime.datetime.now()
        if code != vercode or now > code_time:
            return render(request, "re_passwd.html", {'error': '验证码无效', 'param':email})
        if password1 != password2:
            return render(request, 're_passwd.html', {'error': '两次密码输入不一致', 'param':email})
        user = pro.user
        user.set_password(password1)
        user.save()
        pro.vercode = ''
        pro.save()
        return HttpResponseRedirect('/login/')
    return render(request, 're_passwd.html')


def send_mail(receiver, subject, content):
    status = 0
    for i in range(5):
        try:
            msg = EmailMessage(subject, content, 'cas@100credit.com', receiver)
            msg.content_subtype = "html"  
            msg.send()
            status = 1
        except smtplib.SMTPRecipientsRefused:
            user = User.objects.get(email=receiver[0])
            content = user.first_name + ":" + user.email + ",申请人邮箱有误，请告知修改."
            msg = EmailMessage("CAS系统假期申请,申请人邮箱错误", content, 'cas@100credit.com', ['lei.xu@100credit.com', 'cas@100credit.com'])
            msg.content_subtype = "html"  
            msg.send()
            status = 1
        except Exception:
            time.sleep(0.2)
        if status == 1:
            break 
    else:
        return None
