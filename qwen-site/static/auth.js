// Формы входа и регистрации: проверяем поля, отправляем JSON на сервер,
// при успехе переходим в чат, при ошибке показываем её под формой.

(function () {
    const errorBox = document.getElementById('form-error');

    function showError(text) {
        errorBox.textContent = text;
        errorBox.hidden = false;
    }

    async function send(url, data, button) {
        errorBox.hidden = true;
        button.disabled = true;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json().catch(function () { return {}; });
            if (response.ok && result.ok) {
                window.location.href = '/';
                return;
            }
            showError(result.error || 'Что-то пошло не так. Попробуйте ещё раз.');
        } catch (e) {
            showError('Сервер не отвечает. Проверьте соединение.');
        }
        button.disabled = false;
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const login = document.getElementById('login').value.trim();
            const password = document.getElementById('password').value;
            if (!login || !password) {
                showError('Введите логин и пароль.');
                return;
            }
            send('/api/login', { login: login, password: password },
                loginForm.querySelector('button'));
        });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const name = document.getElementById('fullname').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;

            if (name.length < 2) { showError('Укажите имя (от 2 символов).'); return; }
            if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { showError('Укажите корректный адрес почты.'); return; }
            if (password.length < 8) { showError('Пароль должен быть не короче 8 символов.'); return; }
            if (password !== confirm) { showError('Пароли не совпадают.'); return; }

            send('/api/register', { name: name, email: email, password: password },
                registerForm.querySelector('button'));
        });
    }
})();
