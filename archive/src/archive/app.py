from flask import Flask, render_template, request, jsonify
import mysql.connector
# from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)  

def connect():
    cnx = mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123")
    return cnx    


@app.route('/user_register', methods=['POST'])
def user_register():
    req = request.get_json()
    cnx = mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123")
    
    name = req['name']
    login = req['email']
    password = req['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    date = (name, login, password_hash)
    cur = cnx.cursor(Buffered=True)
    try:
        rows = cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)', date)
    except:
        return {'result':False}
    
    cnx.commit()
    cnx.close()
    return {'result':True, 'id':cur.lastrowid}
    return 'vse ok'

# # Fetch one result
# row = cur.fetchone()
# print("Current date is: {0}".format(row[0]))

# # Close connection
# cnx.close()

@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')
app.run()

@app.route('/user_autorization', methods=['POST'])
def user_autorization():
    req = request.get_json()
    cnx = connect()

    login = req['email']
    password = req['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    date = (login, password_hash)
    cur = cnx.cursor()
    try:
        rows = cur.execute('SELECT * FROM users WHERE email=%s AND password_hash=$s', date)
    except:
        return {'result':False}
    
    cnx.commit()
    cnx.close()
    return {'result':True, 'user':cur.fetchall()}
    return 'vse ok'