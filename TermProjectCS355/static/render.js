$(function render(){
    $.ajax({
        dataType: "json",
        url: "/admin_result",
        success: function (data) {
            $("#DBValues").append(data);
        }
    });
});