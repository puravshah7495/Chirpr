$(function() {
    $('#register_form').submit(function(event) {
        var username = $('#username').val();
        var password = $('#password').val();
        var email = $('#email').val();
        $.post('/adduser', {
            username: username,
            password: password,
            email: email
        }, 
        function(data, status) {
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
});