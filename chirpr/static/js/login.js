$(function() {
    $("#login_form").submit(function(event) {
        var username = $('#username').val();
        var password = $('#password').val();

        $.post('/login', {
            username: username,
            password: password
        }, function(data, status) {
            if (status === "success") {
                if (data.status === "OK") {
                    window.location="/"
                } else {
                    $("#errors").text(data.error); 
                }
            }
        });
        return false;
    });
})