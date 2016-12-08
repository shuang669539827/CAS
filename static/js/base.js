/*
 *  CAS 100credit
 */

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


function show_apply_modal(modalid){
    var modal = $(modalid);
    modal.modal('show');
    modal.find(".modal-body input[name='contact-name']").val('');
    modal.find(".modal-body select[name='contact-pos']").val('');
    modal.find(".modal-body input[name='contact-tel']").val('');
    modal.find(".modal-body input[name='contact-mobile']").val('');
    modal.find(".modal-body input[name='contact-mail']").val('');
}