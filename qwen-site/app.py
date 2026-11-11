import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from collections import defaultdict, deque
from functools import wraps

import mysql.connector
import requests
from dotenv import load_dotenv
from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, session, stream_with_context, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))


# ----------------------------------------------------------------------------
# Настройки
# ----------------------------------------------------------------------------

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', ''),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'database': os.environ.get('DB_NAME', ''),
    'user': os.environ.get('DB_USER', ''),
    'password': os.environ.get('DB_PASSWORD', ''),
    'connection_timeout': 10,
}

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen3:4b')

MAX_HISTORY_MESSAGES = 30      # сколько последних сообщений диалога отправлять модели
MAX_MESSAGE_LENGTH = 8000      # максимальная длина одного сообщения, символов

SECRET_KEY = os.environ.get('SECRET_KEY', '')
if len(SECRET_KEY) < 16:
    raise RuntimeError(
        'В файле .env не задан SECRET_KEY (или он слишком короткий). '
        'Сгенерируйте его командой из README.md.')

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,   # сессия живёт 7 дней
    MAX_CONTENT_LENGTH=1024 * 1024,                # запросы не больше 1 МБ
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)


HASH_NAME = 'pbkdf2_sha256'
HASH_ITERATIONS = 600_000


def hash_password(password, salt=None, iterations=HASH_ITERATIONS):
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return '{}${}${}${}'.format(
        HASH_NAME, iterations,
        base64.b64encode(salt).decode('ascii'),
        base64.b64encode(digest).decode('ascii'))


def check_password(password, stored):
    """True, если пароль подходит к строке из столбца password_hash."""
    try:
        name, iterations, salt_b64, _ = stored.split('$')
        if name != HASH_NAME:
            return False
        expected = hash_password(password, base64.b64decode(salt_b64), int(iterations))
    except (ValueError, AttributeError, TypeError):
        return False
    return hmac.compare_digest(expected, stored)


DUMMY_HASH = hash_password(secrets.token_hex(8))


# ----------------------------------------------------------------------------
# База данных
# ----------------------------------------------------------------------------

def db_connect():
    return mysql.connector.connect(**DB_CONFIG)


def db_find_users(login):
    """Все пользователи, у которых имя или почта совпадают с login."""
    cnx = db_connect()
    try:
        cur = cnx.cursor()
        cur.execute(
            'SELECT `username`, `email`, `password_hash` FROM `users` '
            'WHERE `username` = %s OR `email` = %s',
            (login, login))
        return cur.fetchall()
    finally:
        cnx.close()


class RegistrationError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def db_create_user(username, email, password_hash):
    cnx = db_connect()
    try:
        cur = cnx.cursor()

        # 1. Имя и почта не должны быть заняты
        cur.execute(
            'SELECT `username`, `email` FROM `users` '
            'WHERE `username` = %s OR `email` = %s '
            'OR `username` = %s OR `email` = %s',
            (username, email, email, username))
        for row in cur.fetchall():
            if str(row[1]).lower() == email.lower():
                raise RegistrationError('Эта почта уже зарегистрирована.', 409)
            raise RegistrationError('Это имя уже занято.', 409)

        # 2. Добавляем пользователя (тот же запрос, что и в исходном примере)
        cur.execute(
            'INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)',
            (username, email, password_hash))
        cnx.commit()

        # 3. Устройство таблицы неизвестно, поэтому проверяем, что хеш записался
        #    целиком. Если столбец оказался слишком коротким и база обрезала
        #    строку, убираем только что добавленную нерабочую запись.
        cur.execute(
            'SELECT `password_hash` FROM `users` WHERE `username` = %s AND `email` = %s',
            (username, email))
        saved = [row[0] for row in cur.fetchall()]
        if password_hash not in saved:
            for broken in saved:
                if broken and password_hash.startswith(str(broken)):
                    cur.execute(
                        'DELETE FROM `users` WHERE `username` = %s AND `email` = %s '
                        'AND `password_hash` = %s',
                        (username, email, broken))
            cnx.commit()
            raise RegistrationError(
                'База данных обрезала хеш пароля: столбец password_hash слишком короткий '
                '(нужно не меньше {} символов).'.format(len(password_hash)), 500)
    finally:
        cnx.close()


def db_error_message(err):
    app.logger.error('Ошибка базы данных: %s', err)
    if getattr(err, 'errno', None) == 1062:      # нарушение уникальности
        return 'Такое имя или почта уже зарегистрированы.', 409
    if getattr(err, 'errno', None) == 1406:      # Data too long
        return ('Значение не помещается в столбец таблицы users '
                '(слишком длинное имя, почта или хеш пароля).'), 500
    return 'База данных недоступна. Попробуйте позже.', 503


# ----------------------------------------------------------------------------
# Защита от перебора паролей: не больше 10 неудачных входов за 10 минут с одного IP
# ----------------------------------------------------------------------------

FAILED_LIMIT = 10
FAILED_WINDOW = 600
_failed_logins = defaultdict(deque)
_failed_lock = threading.Lock()


def too_many_failures(ip):
    now = time.time()
    with _failed_lock:
        attempts = _failed_logins[ip]
        while attempts and now - attempts[0] > FAILED_WINDOW:
            attempts.popleft()
        return len(attempts) >= FAILED_LIMIT


def remember_failure(ip):
    with _failed_lock:
        _failed_logins[ip].append(time.time())


# ----------------------------------------------------------------------------
# Страницы
# ----------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify(error='Нужно войти в аккаунт.'), 401
            return redirect(url_for('login_page'))
        return view(*args, **kwargs)
    return wrapper


@app.get('/')
@login_required
def chat_page():
    return render_template('chat.html', username=session['user'], model=OLLAMA_MODEL)


@app.get('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('chat_page'))
    return render_template('login.html', model=OLLAMA_MODEL)


@app.get('/register')
def register_page():
    if 'user' in session:
        return redirect(url_for('chat_page'))
    return render_template('registration.html', model=OLLAMA_MODEL)


@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ----------------------------------------------------------------------------
# Регистрация и вход
# ----------------------------------------------------------------------------

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def start_session(username, email):
    session.clear()
    session.permanent = True
    session['user'] = username
    session['email'] = email


@app.post('/api/register')
def api_register():
    req = request.get_json(silent=True) or {}
    name = str(req.get('name', '')).strip()
    email = str(req.get('email', '')).strip().lower()
    password = str(req.get('password', ''))

    if not 2 <= len(name) <= 50:
        return jsonify(error='Имя должно быть длиной от 2 до 50 символов.'), 400
    if '@' in name:
        return jsonify(error='В имени нельзя использовать символ @.'), 400
    if len(email) > 100 or not EMAIL_RE.match(email):
        return jsonify(error='Укажите корректный адрес почты.'), 400
    if not 8 <= len(password) <= 200:
        return jsonify(error='Пароль должен быть не короче 8 символов.'), 400

    try:
        db_create_user(name, email, hash_password(password))
    except RegistrationError as err:
        return jsonify(error=err.message), err.status
    except mysql.connector.Error as err:
        message, status = db_error_message(err)
        return jsonify(error=message), status

    start_session(name, email)
    return jsonify(ok=True)


@app.post('/api/login')
def api_login():
    req = request.get_json(silent=True) or {}
    login = str(req.get('login', '')).strip()
    password = str(req.get('password', ''))
    ip = request.remote_addr or 'unknown'

    if not login or not password:
        return jsonify(error='Введите логин и пароль.'), 400
    if too_many_failures(ip):
        return jsonify(error='Слишком много неудачных попыток. Подождите 10 минут.'), 429

    try:
        rows = db_find_users(login)
    except mysql.connector.Error as err:
        message, status = db_error_message(err)
        return jsonify(error=message), status

    user = None
    for username, email, password_hash in rows:
        if check_password(password, password_hash):
            user = (username, email)
            break
    if not rows:
        check_password(password, DUMMY_HASH)

    if user is None:
        remember_failure(ip)
        return jsonify(error='Неверный логин или пароль.'), 401

    start_session(*user)
    return jsonify(ok=True)


# ----------------------------------------------------------------------------
# Чат
# ----------------------------------------------------------------------------

class ThinkTagSplitter:

    def __init__(self):
        self.buffer = ''
        self.in_think = False

    def feed(self, text):
        result = []
        self.buffer += text
        while True:
            tag = '</think>' if self.in_think else '<think>'
            kind = 'thinking' if self.in_think else 'content'
            pos = self.buffer.find(tag)
            if pos >= 0:
                if pos:
                    result.append((kind, self.buffer[:pos]))
                self.buffer = self.buffer[pos + len(tag):]
                self.in_think = not self.in_think
                continue
            # В конце может оказаться начало тега ("<thi") - придержим его до следующего куска
            keep = 0
            for size in range(min(len(tag) - 1, len(self.buffer)), 0, -1):
                if tag.startswith(self.buffer[-size:]):
                    keep = size
                    break
            ready = self.buffer[:len(self.buffer) - keep]
            if ready:
                result.append((kind, ready))
            self.buffer = self.buffer[len(self.buffer) - keep:]
            return result

    def flush(self):
        rest, self.buffer = self.buffer, ''
        return [('thinking' if self.in_think else 'content', rest)] if rest else []


def clean_messages(raw):
    """Оставляет от присланной истории только то, что можно передать модели."""
    if not isinstance(raw, list):
        return []
    messages = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role, content = item.get('role'), item.get('content')
        if role not in ('user', 'assistant') or not isinstance(content, str):
            continue
        content = content.strip()
        if content:
            messages.append({'role': role, 'content': content[:MAX_MESSAGE_LENGTH]})
    messages = messages[-MAX_HISTORY_MESSAGES:]
    while messages and messages[0]['role'] != 'user':
        messages.pop(0)
    return messages


def event(kind, text=''):
    """Одна строка потока, который читает chat.js."""
    return json.dumps({'type': kind, 'text': text}, ensure_ascii=False) + '\n'


# Модель работает в один поток, поэтому отвечаем только на один запрос одновременно
generation_lock = threading.Lock()


@app.post('/api/chat')
@login_required
def api_chat():
    req = request.get_json(silent=True) or {}
    messages = clean_messages(req.get('messages'))
    if not messages or messages[-1]['role'] != 'user':
        return jsonify(error='Пустое сообщение.'), 400

    def generate():
        if not generation_lock.acquire(blocking=False):
            yield event('error', 'Модель сейчас отвечает на другой запрос. Попробуйте чуть позже.')
            return
        try:
            payload = {'model': OLLAMA_MODEL, 'messages': messages, 'stream': True, 'think': True}
            # timeout: 5 секунд на соединение, до 10 минут ожидания очередного куска ответа
            with requests.post(OLLAMA_URL + '/api/chat', json=payload,
                               stream=True, timeout=(5, 600)) as resp:
                if resp.status_code != 200:
                    try:
                        detail = resp.json().get('error', '')
                    except ValueError:
                        detail = ''
                    yield event('error', 'Ollama вернула ошибку {}. {}'.format(resp.status_code, detail))
                    return

                splitter = ThinkTagSplitter()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if chunk.get('error'):
                        yield event('error', 'Ошибка Ollama: {}'.format(chunk['error']))
                        return
                    message = chunk.get('message') or {}
                    if message.get('thinking'):
                        yield event('thinking', message['thinking'])
                    if message.get('content'):
                        for kind, text in splitter.feed(message['content']):
                            yield event(kind, text)
                    if chunk.get('done'):
                        break
                for kind, text in splitter.flush():
                    yield event(kind, text)
                yield event('done')
        except requests.ConnectionError:
            yield event('error', 'Не удалось подключиться к Ollama. Проверьте, что она запущена.')
        except requests.RequestException as err:
            app.logger.error('Ошибка запроса к Ollama: %s', err)
            yield event('error', 'Соединение с Ollama прервалось.')
        except ValueError:
            yield event('error', 'Ollama прислала непонятный ответ.')
        finally:
            # Сюда попадаем и тогда, когда пользователь нажал "Стоп" или закрыл вкладку:
            # соединение с Ollama закрывается, и модель прекращает генерацию.
            generation_lock.release()

    return Response(
        stream_with_context(generate()),
        mimetype='application/x-ndjson',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


if __name__ == '__main__':
    # Запуск для проверки: python app.py
    # Для постоянной работы используйте gunicorn (см. README.md)
    app.run(host='127.0.0.1', port=8000, threaded=True)
