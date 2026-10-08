$(document).ready(function() {

    $('#67').on('submit', function(e) {
        e.preventDefault();
        let err = 0;

        
        if ($('#fullname').val().trim() === '' || $('#password').val().trim() !== $('#confirm_password').val().trim()) {
            err = 1;
        }

        if (err === 0) {
            $.ajax({
                url: '/user_register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    name: $('#fullname').val(),
                    password: $('#password').val(),
                    email: $('#email').val()
                })
            })
            .done(function(data) {
                if (data.result) {
                    
                    window.location.href = '/login';
                } else {
                    alert('Что-то пошло не так при регистрации');
                }
            })
            .fail(function() {
                alert('Ошибка сервера');
            });
        }
    });

    
    $('#76').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            
            url: '/user_autorization', 
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: $('#email').val(),
                password: $('#password').val()
            })
        })
        .done(function(data) {
            if (data.result) {
                window.location.href = '/';
            } else {
                alert('Неверный email или пароль');
            }
        })
        .fail(function() {
            alert('Ошибка сервера');
        });
    });
});
