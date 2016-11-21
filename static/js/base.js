

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