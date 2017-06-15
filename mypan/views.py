# -*- coding: utf-8 -*-
import os
import json
import logging
import time
import zipfile
import shutil
import HTMLParser

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from models import MaxSize
from utils import name_size
from utils import folder_tree

# Create your views here.

logger = logging.getLogger('daserr')

NOW_PATH = os.getcwd() + '/yunpath'
max_up_size = 51200000
if MaxSize.objects.all().first():
    max_up_size = MaxSize.objects.all().first().size


@login_required
def home(request):
    username = request.user.username
    storepath = os.path.join(NOW_PATH, username)

    if not os.path.exists(storepath):
        os.makedirs(storepath)

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if '.'.join(ip.split('.')[:-1]) in ['192.168.162', '192.168.190', '192.168.254']:
        return HttpResponse('IP限制')

    response = render_to_response('mypan-home.html', {'username': username})
    response.set_cookie("storepath", storepath)
    return response


@login_required
def uploadfile(request):

    def handle_uploaded_file(sf, rootpath):
        relative_path = encory(request.POST['relative_path'])
        filepath = os.path.join(rootpath, relative_path, sf.name)

        destination = open(filepath, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

    try:
        if request.method == "POST":

            f = request.FILES['InputFile']

            ext = os.path.splitext(f.name)[1]
            if ext not in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.pdf', '.rar', '.zip']:
                return HttpResponse(json.dumps({'status': 'error',
                                                'msg': '只允许上传doc,docx,xls,xlsx,ppt,pptx,txt,pdf,rar,zip文件'},
                                    ensure_ascii=False),
                                    content_type='application/json')

            if f.size > max_up_size:
                return HttpResponse(json.dumps({'status': 'error',
                                                'msg': '文件大小不能超过50M'},
                                    ensure_ascii=False),
                                    content_type='application/json')

            if request.POST['yunpan_type'] == 'self':
                storepath = request.COOKIES["storepath"]
            elif request.POST['yunpan_type'] == 'share':
                storepath = os.path.join(NOW_PATH, 'share_folder')
            else:
                storepath = os.path.join(NOW_PATH, 'department'+str(request.user.pro.department.id))

            handle_uploaded_file(f, storepath)

            return HttpResponse(json.dumps({'status': 'true'},
                                ensure_ascii=False),
                                content_type='application/json')

        else:
            return HttpResponse('need post method')
    except Exception as e:
        logger.exception(e)
        return HttpResponse(json.dumps({'status': 'error', 'msg': e.message},
                            ensure_ascii=False),
                            content_type='application/json')


@login_required
def download_file(request):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    filename_list = encory(request.POST.get('filename')).split(';;;')[:-1]
    relative_path = encory(request.POST.get('relative_path'))
    if request.POST['yunpan_type'] == 'self':
        storepath = request.COOKIES["storepath"]
    elif request.POST['yunpan_type'] == 'share':
        storepath = os.path.join(NOW_PATH, 'share_folder')
    else:
        storepath = os.path.join(NOW_PATH, 'department' + str(request.user.pro.department.id))
    first_file = filename_list[0].split(',')
    is_delete = False
    if len(filename_list) == 1 and first_file[1] == '0':
        down_file = os.path.join(storepath, relative_path, first_file[0])
        filename = first_file[0]
    else:
        all_file = []
        for item in filename_list:
            item_list = item.split(',')
            path = os.path.join(storepath, relative_path, item_list[0])
            if os.path.isfile(path):
                all_file.append(path)
            else:
                all_file.extend(folder_tree(path))
        time_stamp = str(time.time())
        down_file = '%s批量下载.zip' % time_stamp
        z = zipfile.ZipFile(down_file, 'w', zipfile.ZIP_DEFLATED)
        for fl in all_file:
            z.write(file, arcname=fl.replace(storepath, ''))
        z.close()
        is_delete = True
        filename = '批量下载.zip'

    response = LogStreamResponse(is_delete, down_file, file_iterator(down_file))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)

    return response


@login_required
def cmd_ls(request):
    if request.POST['yunpan_type'] == 'self':
        storepath = request.COOKIES["storepath"]
    elif request.POST['yunpan_type'] == 'share':
        storepath = os.path.join(NOW_PATH, 'share_folder')
        if not os.path.exists(storepath):
            os.makedirs(storepath)
    else:
        department_id = request.user.pro.department.id
        storepath = os.path.join(NOW_PATH, 'department'+str(department_id))
        if not os.path.exists(storepath):
            os.makedirs(storepath)

    relative_path = encory(request.POST['relative_path'])
    select_folder = os.path.join(storepath, relative_path)
    if not os.path.exists(select_folder):
        response_dict = {'find': 0}
        os.makedirs(select_folder)
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')

    result = name_size(select_folder)
    if len(result) == 0:
        response_dict = {'find': 0}
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')

    response = HttpResponse(json.dumps(result, ensure_ascii=False),
                            content_type='application/json')

    return response


@login_required
def create_file(request):
    if request.POST['yunpan_type'] == 'self':
        storepath = request.COOKIES["storepath"]
    elif request.POST['yunpan_type'] == 'share':
        storepath = os.path.join(NOW_PATH, 'share_folder')
    else:
        storepath = os.path.join(NOW_PATH, 'department' + str(request.user.pro.department.id))
    relative_path = request.POST['relative_path']
    filename = request.POST['filename']
    file_path = os.path.join(storepath, relative_path, filename)
    if not os.path.exists(file_path):
        try:
            os.mkdir(file_path)
        except Exception as e:
            logger.exception(e)
            response_dict = {'status': 'fail', 'msg': '创建失败'}
            return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                                content_type='application/json')

        nowtime = os.stat(file_path).st_mtime
        ctime = time.localtime(nowtime)
        ctime_str = time.strftime('%Y-%m-%d %H:%M', ctime)

        response_dict = {'status': 'success', 'msg': '创建文件夹成功',
                         'filename': filename, 'ctime': ctime_str}
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')
    else:
        response_dict = {'status': 'fail', 'msg': '文件夹已经存在'}
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')


@login_required
def delete_file(request):
    if request.POST['yunpan_type'] == 'self':
        storepath = request.COOKIES["storepath"]
    elif request.POST['yunpan_type'] == 'share':
        storepath = os.path.join(NOW_PATH, 'share_folder')
    else:
        storepath = os.path.join(NOW_PATH, 'department' + str(request.user.pro.department.id))
    str_encory = encory(request.POST.get('filename'))
    filename_list = str_encory.split(';;;')[:-1]
    relative_path = encory(request.POST.get('relative_path'))
    for item in filename_list:
        try:
            item_list = item.split(',')
            path = os.path.join(storepath, relative_path, item_list[0])
            if item_list[1] == '0':
                os.remove(path)
            else:
                shutil.rmtree(path)
        except Exception as e:
            logger.exception(e)
    response_dict = {'status': 'success', 'msg': '删除文件夹成功'}
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                        content_type='application/json')


@login_required
def rename(request):
    if request.POST['yunpan_type'] == 'self':
        storepath = request.COOKIES["storepath"]
    elif request.POST['yunpan_type'] == 'share':
        storepath = os.path.join(NOW_PATH, 'share_folder')
    else:
        storepath = os.path.join(NOW_PATH, 'department' + str(request.user.pro.department.id))
    oldname = encory(request.POST.get('oldname'))
    newname = encory(request.POST.get('newname'))
    relative_path = encory(request.POST.get('relative_path'))

    old_path = os.path.join(storepath, relative_path, oldname)
    new_path = os.path.join(storepath, relative_path, newname)
    try:
        os.rename(old_path, new_path)
        response_dict = {'status': 'success', 'msg': '修改名字成功'}
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')
    except Exception as e:
        logger.exception(e)
        response_dict = {'status': 'fail', 'msg': '修改名字失败'}
        return HttpResponse(json.dumps(response_dict, ensure_ascii=False),
                            content_type='application/json')


def encory(source):
    return HTMLParser.HTMLParser().unescape(source)


class LogStreamResponse(StreamingHttpResponse):

    def __init__(self, is_delete, zip_filename, *args, **kwargs):
        self.zip_filename = zip_filename
        self.is_delete = is_delete
        super(LogStreamResponse, self).__init__(*args, **kwargs)

    def close(self):
        if os.path.exists(self.zip_filename) and self.is_delete is True:
            os.remove(self.zip_filename)
        super(LogStreamResponse, self).close()
