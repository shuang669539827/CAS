/*
 *  CAS 100credit
 */

bootbox.setLocale("zh_CN");

function loadgif(flag){
    var oLoading = $('#loading');
    if (oLoading){
        if(flag){
            oLoading.css('display', 'block');
        }else{
            oLoading.css('display', 'none');
        }
    }
}

jQuery.fn.disable = function() {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function(opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};

function clckimg(obj) {
  var ctimes=obj.ctimes;
  if(parseInt(ctimes) > 0)
  {
    return false;
  }
  else{
    obj.ctimes="1";
  }
}

function submit(){
	url = '/eat/list/';
	var name  = $("#username").val();
	var floor = $("#floor").val();
	var num = $("#num").val();
	if (name == "") {
		alert("name is not null");
	}else if (floor == "") {
		alert("floor is not null");
	}else if (num == "") {
		alert("num is not null");
	}else {
	$.getJSON(url,{"name":name, "floor":floor, "num":num},function(result){
            if (result.msg == 0){
                alert('error');
                location.reload();
            }
        });
    }
}

function contains(arr, obj) {
    var i = arr.length;
    while (i--) {
        if (arr[i] === obj) {
            return true;
        }
    }
    return false;
}


function checkfile(obj){
    var fileExt = obj.value.substr(obj.value.lastIndexOf(".")).toLowerCase();
    var myarray = new Array(".doc", ".docx", ".pdf");
    if(contains(myarray, fileExt)){
        var fileSize = 0;
        var isIE = /msie/i.test(navigator.userAgent) && !window.opera;
        if (isIE && !obj.files) {
             var filePath = obj.value;
             var fileSystem = new ActiveXObject("Scripting.FileSystemObject");
             var file = fileSystem.GetFile (filePath);
             fileSize = file.Size;
        }else {
             fileSize = obj.files[0].size;
        }
        if(fileSize>=15360000){
            bootbox.alert("最大尺寸为15M，请重新上传");
            obj.outerHTML=obj.outerHTML;
            return false;
        }
    }else {
        bootbox.alert('请上传doc、docx、pdf格式附件');
        obj.outerHTML=obj.outerHTML;
        return false;
    }

}


function show_apply_modal(modalid){
    var modal = $(modalid);
    modal.modal('show');
    modal.find(".modal-body input[name='contact-name']").val('');
    modal.find(".modal-body select[name='contact-pos']").val('');
    modal.find(".modal-body input[name='contact-tel']").val('');
    modal.find(".modal-body input[name='contact-mobile']").val('');
    modal.find(".modal-body input[name='contact-mail']").val('');
}

function init (){
	setTimeout(function(){
		//var flag ;
		 var width = screen.availWidth;
		if(width<=768){
		
		var dom=document.getElementsByClassName('nav')[1];
		var odom = document.getElementsByClassName('main')[0];
		
		if(document.getElementsByClassName('page-header')[0]&&(document.getElementsByClassName('page-header')[0].innerHTML=='待审批'||document.getElementsByClassName('page-header')[0].innerHTML=='请选择申请假期类型')){
			
			//flag = 1;
			var cdom = document.getElementsByClassName('page-header')[0];
		}else{
			var cdom = document.getElementsByClassName('sub-header')[0];
		}
//		(document.getElementsByClassName('sub-header')[0]&&flag!=1){
//			
//		}
		
		odom.insertBefore(dom,cdom);
	}
	},500)
	
	
}

// init();
