from flask import Flask, render_template, request
import mysql.connector
import hashlib

app = Flask(__name__)

def connect():
    return mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123"
    )

@app.route('/user_register', methods=['POST'])
def user_register():
    
    if request.is_json:
        req = request.get_json()
    else:
        req = request.form
    cnx = connect()
    
    name = req['name']
    login = req['email']
    password = req['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    date = (name, login, password_hash)
    
    cur = cnx.cursor(buffered=True)
    try:
        cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)', date)
        cnx.commit()
        return {'result': True, 'id': cur.lastrowid}
    except mysql.connector.Error:
        return {'result': False}
    finally:
        cur.close()
        cnx.close()

@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route('/user_autorization', methods=['POST'])
def user_autorization():
    if request.is_json:
        req = request.get_json()
    else:
        req = request.form
    cnx = connect()

    login = req['email']
    password = req['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    date = (login, password_hash)
    
    cur = cnx.cursor(buffered=True)
    try:
        cur.execute('SELECT * FROM users WHERE email=%s AND password_hash=%s', date)
        user = cur.fetchone() # Берем одну запись
        
        if user: # Если пользователь найден
            return {'result': True, 'user': user}
        else: # Если пароль или логин неверные
            return {'result': False, 'error': 'Неверный email или пароль'}
            
    except mysql.connector.Error as err:
        print(f"Ошибка БД: {err}")
        return {'result': False}
    finally:
        cur.close()
        cnx.close()

app.run(debug=True)