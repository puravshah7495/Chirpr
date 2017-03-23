$(function() {
    $("#logout").click(function() {
        $.post('/logout', function(data, status) {
            window.location="/"
        });
    });
});