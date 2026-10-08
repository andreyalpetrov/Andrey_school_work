$(document).ready(function() {
    // Обработчик формы регистрации (предположительно id="67")
    $('#67').on('submit', function(e) {
        e.preventDefault();
        let err = 0;

        // Проверка: пустое имя ИЛИ пароли не совпадают
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
                    // ИСПРАВЛЕНО: href - это свойство, а не функция
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

    // Обработчик формы авторизации (предположительно id="76")
    $('#76').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            // ИСПРАВЛЕНО: для авторизации нужен другой URL
            url: '/user_autorization', 
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                // В форме логина обычно нет fullname и confirm_password
                email: $('#email').val(),
                password: $('#password').val()
            })
        })
        .done(function(data) {
            if (data.result) {
                window.location.href = '/'; // Или на главную страницу
            } else {
                alert('Неверный email или пароль');
            }
        })
        .fail(function() {
            alert('Ошибка сервера');
        });
    });
});
