import os
import time


def name_size(path):
    result = []
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp):
            filetype = os.path.splitext(filename)[1]
            size = float(os.path.getsize(fp))
            unit = 'B'
            if size > 1024:
                size = float(size / 1024)
                unit = 'KB'

            if size > 1024:
                size = float(size / 1024)
                unit = 'MB'
            if size > 1024:
                size = float(size / 1024)
                unit = 'G'

            size = '%.2f %s' % (size, unit)

        else:
            size = '-'
            filetype = 'folder'
        nowtime = os.stat(fp).st_mtime
        ctime = time.localtime(nowtime)
        ctime_str = time.strftime('%Y-%m-%d %H:%M', ctime)
        info = {'filename': filename, 'size': size,
                'filetype': filetype, 'ctime': ctime_str}
        if filetype == 'folder':
            result.insert(0, info)
        else:
            result.append(info)
    return result


def folder_tree(path):
    tree_list = []
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp):
            tree_list.append(fp)
        else:
            tree_list.extend(folder_tree(fp))
    return tree_list
