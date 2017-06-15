function event_listeners() {


    $('.dialog-confirm').on('click', '.icon-close', function(e) {
        $('.module-canvas').css('display', 'none');
        $('.dialog-confirm').css('display', 'none');
        e.stopPropagation();
    });

    $('.dialog-confirm').on('click', '.yes', function(e) {
        $('.module-canvas').css('display', 'none');
        $('.dialog-confirm').css('display', 'none');

        var filename = ''
        for (var i = 0; i < checkbox_list.length; i++) {
            filename = filename + $(checkbox_list[i]).parent().find('.file-name a').html() + ',' + $(checkbox_list[i]).parent().find('.file-name a').attr('is-folder') + ';;;';


        }
        var url = '/yunpan/deletefile/';
        delete_file(url, filename, relative_path);
        checkbox_list = [];
        e.stopPropagation();
    });

    $('.dialog-confirm').on('click', '.no', function(e) {
        $('.module-canvas').css('display', 'none');
        $('.dialog-confirm').css('display', 'none');
        e.stopPropagation();
    });


    $('#left-nav').on('click', 'li', function(e) {

        $('#left-nav > li > a').removeClass('active');

        var data_type = '';
        if (e.target.tagName == 'SPAN') {
            data_type = $(e.target).attr('data-type');
            $(e.target).parent().addClass('active');

        } else {
            data_type = $(e.target).find('span').attr('data-type');
            $(e.target).addClass('active');

        }
        var list_view = $('.list-view-wrapper dd');
        if (data_type == 'all') {

            for (var i = 1; i < list_view.length; i++) {
                var obj = $(list_view[i]);
                obj.css('display', 'block');
            }
            return

        }

        for (var i = 1; i < list_view.length; i++) {
            var obj = $(list_view[i]);
            console.log(obj.hasClass(data_type));
            if (obj.attr('data-kind') == data_type) {
                obj.css('display', 'block');
            } else {
                obj.css('display', 'none');
            }

        }

    });

    $('.header-link > span > a').on('click', function(e) {
        console.log('click title');
        checkbox_list = [];
        $('.header-link > span > span').removeClass('subscript');
        $(e.target).parent().find('span').addClass('subscript');
        if ($(e.target).attr('data-type') == 'wangpan') {
            history_path = [];
            relative_path = history_path.join('/');
            yunpan_type = 'self';
            flush_catalog(relative_path);
        } else if ($(e.target).attr('data-type') == 'share') {
            history_path = [];
            relative_path = history_path.join('/');
            yunpan_type = 'share';
            flush_catalog(relative_path);
        } else if ($(e.target).attr('data-type') == 'department') {
            history_path = [];
            relative_path = history_path.join('/');
            yunpan_type = 'department';
            flush_catalog(relative_path);
        }


        e.stopPropagation();

    });


    $('.back-parent').on('click', function() {

        history_path.pop();
        relative_path = history_path.join('/');
        console.log(relative_path);
        $('.no-result-file-download').css('display', 'none');
        checkbox_list = [];
        flush_catalog(relative_path);

    });

    $('#createfile').on('click', function() {
        console.log('createfile createfile');
        $('.no-result-file-download').css('display', 'none');
        for (var i = 0; i < checkbox_list.length; i++) {
            $(checkbox_list[i]).css('background-position', "9px 15px");
            $(checkbox_list[i]).attr('action-check', '0');
        }

        checkbox_list = [];
        $('.item-first').css('display', 'block');
        var top = $('.item-first').position().top;
        $('.module-edit-name').css('top', top);
        $('.module-edit-name').css('display', 'block');
        $('#new-dir-box').focus().val('新建文件夹');

    });

    $('#delete-file').on('click', function() {
        console.log('deletefile deletefile');
        if (checkbox_list.length == 0) {
            error_tip('请至少选中一个文件');
            return
        }

        $('.module-canvas').css('display', 'block');
        $('.dialog-confirm').css('display', 'block');

    });



    $('#download').on('click', function() {
        console.log('download download');
        if (checkbox_list.length == 0) {
            error_tip('请至少选中一个文件');
            return
        }
        var filename = ''
        for (var i = 0; i < checkbox_list.length; i++) {
            filename = filename + $(checkbox_list[i]).parent().find('.file-name a').html() + ',' + $(checkbox_list[i]).parent().find('.file-name a').attr('is-folder') + ';;;';


        }
        var url = '/yunpan/downloadfile/';

        download_file(url, filename, relative_path);

    });


    $('#rename').on('click', function() {
        if (checkbox_list.length == 1) {
            var oldname = $(checkbox_list[0]).parent().find('.file-name a').html();
            $('#new-dir-box').focus().val(oldname);
            var top = $(checkbox_list[0]).parent().position().top;
            $('.module-edit-name').css('top', top);
            $('.module-edit-name').css('display', 'block');

            /*                var url = '/yunpan/rename';
                            rename(url, filename, relative_path);*/

        } else {
            error_tip('只能选中单个文件');
        }

    });



    $('.sure').on('click', function() {
        console.log('sure sure sure sure');
        var newname = $('#new-dir-box').focus().val();
        if (!filter_blank_name(newname)) {
            return
        }
        if (checkbox_list.length == 0) {
            create_file('/yunpan/createfile/', newname, relative_path);
        } else if (checkbox_list.length == 1) {
            var oldname = $(checkbox_list[0]).parent().find('.file-name a').html()
            rename('/yunpan/rename/', oldname, newname, relative_path);
            checkbox_list = [];
        }

    });

    $('.cancel').on('click', function() {
        $('.item-first').css('display', 'none');
        $('.module-edit-name').css('display', 'none');
        if ($('.list-view-wrapper dd').length == 1) {
            $('.no-result-file-download').css('display', 'block');
        }
        console.log('cancel cancel cancel');
    });


    $('.dialog-control').on('click', '.icon-minimize', function(e) {
        $('.dialog-web-uploader').addClass('dialog-web-short');
        var target = e.target;
        $(target).removeClass('con-minimize');
        $(target).addClass('icon-maximizing');
        console.log('icon-minimize');
    });

    $('.dialog-control').on('click', '.icon-close', function() {

        console.log('icon-close');
        $('.dialog-web-uploader').css('display', 'none');
    });

    $('.dialog-control').on('click', '.icon-maximizing', function(e) {
        $('.dialog-web-uploader').removeClass('dialog-web-short');
        var target = e.target;
        $(target).removeClass('icon-maximizing');
        $(target).addClass('con-minimize');
        console.log('icon-minimize');
    });

    $('.module-history-list').on('click', '.back-index', function() {
        history_path = [];
        relative_path = history_path.join('/');
        flush_catalog(relative_path);
        $('.historylistmanager-history').css('display', 'none');
    });

    $('.module-history-list').on('click', '.back-folder', function(e) {
        relative_path = $(e.target).attr('title');
        if (relative_path[0] == '/') {
            relative_path = relative_path.slice(1);
        }
        history_path = relative_path.split('/');
        flush_catalog(relative_path);
    });


    $('.list-view-wrapper').on('click', '.file-name a', function(e) {
        //$('.file-name').on('click', 'a', function(e) {
        var target = e.target;
        var is_folder = $(target).attr('is-folder');
        if (is_folder == "1") {
            floder_name = $(target).html();
            history_path.push(floder_name);
            relative_path = history_path.join('/');
            console.log(relative_path);
            flush_catalog(relative_path);

        }
    });

    $('.list-view-wrapper').on('click', '.checkbox', checkbox);
    $('.upload-btn').on('change', upload);


}

function upload(e) {

    var target = e.target;
    console.log('change change change change');

    var formData = new FormData();
    formData.append("InputFile", target.files[0]);
    var filename = target.files[0].name;
    var filesize = target.files[0].size;
    var show_path = '&nbsp';
    if (relative_path != '') {
        show_path = relative_path;
    }

    var html = '<li class="file-list process-li">\
                        <div class="process"></div>\
                        <div class="info">\
                            <div class="file-name" title="{0}" style="width:150px;">\
                                <span>{0}</span>\
                            </div>\
                            <div class="file-size">{1} B</div>\
                            <div class="file-status"></div>\
                        </div>\
                    </li>'.format(filename, filesize);


    $('.uploader-list ul').append(html);



    $('.dialog-web-uploader .file-name span:last').html(filename);
    $('.dialog-web-uploader').css('display', 'block');
    var url = '/yunpan/uploadfile/'
    formData.append('relative_path', relative_path);
    formData.append('yunpan_type', yunpan_type);
    var status_bar = $('.uploader-list ul li:last');
    var xhr = $.ajax({

        url: url,
        type: "POST",
        data: formData,
        /**
         *必须false才会自动加上正确的Content-Type
         */
        contentType: false,
        /**
         * 必须false才会避开jQuery对 formdata 的默认处理
         * XMLHttpRequest会对 formdata 进行正确的处理
         */
        processData: false,

        　　　　xhr: function() {　　　　　　
            var xhr = $.ajaxSettings.xhr();　　
            if (onprogress && xhr.upload) {　　　　　　　　
                xhr.upload.addEventListener("progress", onprogress.bind(null, status_bar), false);　　　　　　　　
                return xhr;　　　　　　
            }
        },

        success: function(data) {
            if (data.status == "true") {
                console.log("上传成功！");
                $(status_bar).find('.file-status').html('上传成功！');

                $(status_bar).find('.process:last').css('display', 'none');
            }
            if (data.status == "error") {
                $(status_bar).find('.file-status').html(data.msg);
            }
            flush_catalog(relative_path);

        },
        error: function(data, status, e) {
            $('.uploader-list .file-status:last').html(data.msg);
            error_tip('上传失败，500错误');

        }
    });
    $(target).val('');


}


function download_file(url, filename, path) {

    console.log(filename);
    $('#download-file').attr("method", "post");
    $('#download-file').attr("action", url);

    $('#download-file input').eq(0).attr('value', filename);
    $('#download-file input').eq(1).attr('value', path);
    $('#download-file input').eq(2).attr('value', yunpan_type);
    $('#download-file').submit();

}

function delete_file(url, filename, path) {

    $.ajax({

        url: url,
        type: "POST",
        data: {
            'filename': filename,
            'relative_path': path,
            'yunpan_type': yunpan_type,
        },
        success: function(data) {
            console.log(data);
            checkbox_list.splice(0, 1);
            flush_catalog(path);
            success_tip(data);
        },
        error: function(data, status, e) {
            error_tip('删除失败，500错误');
        }

    });
}


function create_file(url, filename, path) {

    $.ajax({
        url: url,
        async: true,
        dataType: 'json',
        type: 'POST',
        data: {
            'relative_path': path,
            'filename': filename,
            'yunpan_type': yunpan_type,
        },

        success: function(data, textStatus) {
            console.log(data);
            $('.item-first').css('display', 'none');
            $('.module-edit-name').css('display', 'none');
            if (data.status == 'success') {

                var html = '<dd class="list-view-item">\
                    <span class="checkbox" action-check="0" >\
                        <span class="icon checksmall"></span>\
                    </span>\
                    <div class="fileicon dir-small"></div>\
                    <div class="file-name" >\
                        <div class="text"><a is-folder="1">{0}</a></div>\
                    </div>\
                    <div class="file-size text" >-</div>\
                    <div class="ctime text" >{1}</div>\
                </dd>'.format(data.filename, data.ctime);
                $('.list-view-wrapper .item-first').after(html);

            }
            success_tip(data);

        },

        error: function(jqXHR, textStatus, errorThrown) {
            error_tip('创建失败，500错误');
        },

    });


}



function rename(url, oldname, newname, path) {

    $.ajax({

        url: url,
        type: "POST",
        data: {
            'oldname': oldname,
            'newname': newname,
            'relative_path': path,
            'yunpan_type': yunpan_type,
        },
        success: function(data) {
            console.log(data);
            flush_catalog(path);
            $('.item-first').css('display', 'none');
            $('.module-edit-name').css('display', 'none');

            success_tip(data);


        },
        error: function(data, status, e) {
            error_tip('重命名失败，500错误');
        }

    });
}








String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{' + i + '\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};


function filter_blank_name(name) {
    console.log(/\S/.test(name));
    if (/\S/.test(name)) {
        return true;
    } else {
        error_tip('不能全空字符串');
        return false;
    }
}


function success_tip(data) {
    $('.module-tip').css('display', 'block');
    $('.module-tip span').html(data.msg);
    setTimeout("$('.module-tip').css('display', 'none');", 3000);

}

function error_tip(msg) {
    $('.module-tip').css('display', 'block');
    $('.module-tip span').html(msg);
    setTimeout("$('.module-tip').css('display', 'none');", 3000);

}

function checkbox(e) {
    console.log('checkbox click');
    var nowbox = e.target;
    if ($(nowbox).attr('action-check') == 0) {
        $(nowbox).css('background-position', "-34px 15px");
        $(nowbox).attr('action-check', '1');
        checkbox_list.push(nowbox);
    } else if ($(nowbox).attr('action-check') == 1) {
        $(nowbox).css('background-position', "9px 15px");
        $(nowbox).attr('action-check', '0');
        for (var i = 0; i < checkbox_list.length; i++) {
            if (checkbox_list[i] === nowbox) {
                checkbox_list.splice(i, 1);
                break;
            }
        }


    }
    console.log(checkbox_list);
}


function onprogress(target, evt) {　　
    var loaded = evt.loaded; //已经上传大小情况 
    var tot = evt.total; //附件总大小 
    //var per =  Math.floor(loaded / tot); //已经上传的百分比 
    var per = loaded / tot
    var width = $(target).width() * per;
    console.log(width);
    $(target).find('.process').css('width', width);
    $(target).find('.file-status').html('%' + Math.floor(per * 100).toString());

    console.log(per);　　
}

function flush_catalog(path) {


    var tag_dd = $('.list-view-wrapper dd');
    if (tag_dd.length > 1) {
        for (var i = 1; i < tag_dd.length; i++) {
            tag_dd[i].remove();
        }
    }

    $.ajax({
        url: '/yunpan/showfile/',
        async: true,
        dataType: 'json',
        type: 'POST',
        data: {
            'relative_path': path,
            'yunpan_type': yunpan_type,
        },
        success: function(data, textStatus) {
            console.log('flush_catalog ' + path);


            $('.historylistmanager-history li').eq(1).empty();

            if (history_path.length > 0) {
                $('.historylistmanager-history li').eq(1).empty();
                var history_html = '<a title="全部文件" class="back-index">全部文件</a><span class="historylistmanager-separator-gt">></span>'
                var tree_path = ''
                for (var i = 0; i < history_path.length - 1; i++) {
                    tree_path = tree_path + '/' + history_path[i];
                    history_html += '<a href="javascript:;" class="back-folder" title="{0}" data-deep="{1}">{2}</a><span class="historylistmanager-separator-gt">></span>'.format(tree_path, i + 1, history_path[i]);
                }
                tree_path = tree_path + '/' + history_path[history_path.length - 1];
                history_html += '<span title="{0}">{1}</span>'.format(tree_path, history_path[history_path.length - 1]);
                $('.historylistmanager-history li').eq(1).append(history_html);
                $('.historylistmanager-history').css('display', 'block');
            } else {
                $('.historylistmanager-history').css('display', 'none');
            }


            if (data.find == 0) {
                $('.no-result-file-download').css('display', 'block');
                $('.history-list-tips').html('共0个');
            } else {
                $('.no-result-file-download').css('display', 'none');
                var html = '';
                $('.history-list-tips').html('共' + data.length + '个');
                for (var i = 0; i < data.length; i++) {

                    var filetype = data[i].filetype;
                    var css_name = '';
                    var kind = '';
                    var is_folder = 0;
                    if (data[i].filetype == 'folder') {
                        css_name = 'dir-small';
                        is_folder = 1;
                    } else if (data[i].filetype == '.doc' ||
                        data[i].filetype == '.docx') {
                        css_name = 'fileicon-small-doc';
                        kind = 'doc';
                    } else if (data[i].filetype == '.zip') {
                        css_name = 'fileicon-small-zip';
                        kind = 'zip';
                    } else if (data[i].filetype == '.txt') {
                        css_name = 'fileicon-small-text';
                        kind = 'other';
                    } else if (data[i].filetype == '.pdf') {
                        css_name = 'fileicon-small-pdf';
                        kind = 'pdf';
                    } else if (data[i].filetype == '.exe') {
                        css_name = 'fileicon-sys-s-exe';
                        kind = 'other';
                    } else if (data[i].filetype == '.rmvb' ||
                        data[i].filetype == '.mtk') {
                        css_name = 'fileicon-small-video';
                        kind = 'video';
                    } else if (data[i].filetype == '.png' ||
                        data[i].filetype == '.img' ||
                        data[i].filetype == '.gif') {
                        css_name = 'fileicon-small-pic';
                        kind = 'pic';
                    } else {
                        css_name = 'default-small';
                        kind = 'other';
                    }


                    html += '<dd class="list-view-item" data-kind="{5}">\
                    <span class="checkbox" action-check="0" >\
                        <span class="icon checksmall"></span>\
                    </span>\
                    <div class="fileicon {3}"></div>\
                    <div class="file-name" >\
                        <div class="text"><a is-folder="{4}">{0}</a></div>\
                    </div>\
                    <div class="file-size text" >{1}</div>\
                    <div class="ctime text" >{2}</div>\
                </dd>'.format(data[i].filename, data[i].size, data[i].ctime, css_name,
                        is_folder, kind);

                }

                $('.list-view-wrapper').append(html);


            }

        },

        error: function(jqXHR, textStatus, errorThrown) {
            console.log("error");

        },

    });
}


$(document).ready(function() {

    checkbox_list = [];
    relative_path = '';
    history_path = [];
    yunpan_type = 'self';

    var win_height = $(window).height();
    var header_height = $(".header").outerHeight(true);
    $('#left-nav').height(win_height - header_height);

    history.pushState(null, null, document.URL);
    window.addEventListener('popstate', function() {
        history.pushState(null, null, document.URL);
    });


    $(window).resize(function() {
        //console.log($(window).height());
        var win_height = $(window).height();
        var view_top = $('.list-view-wrapper').offset().top;
        var distance = win_height - view_top;
        if (distance > 100) {
            /*                if(distance> $('.list-view-wrapper').height()){

                            }*/

            $('.list-view-wrapper').height(distance);
        }
    });
    flush_catalog(relative_path);
    event_listeners();

});
