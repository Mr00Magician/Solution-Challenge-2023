from flask import Flask, render_template, request, redirect, url_for
from pyrebase import initialize_app

firebase_config = {
    'apiKey': "AIzaSyBpvrG-ZXQ5GciT2hQMn02S6rZ_ocdOMN8",
    'authDomain': "ideaverse-80ef2.firebaseapp.com",
    'projectId': "ideaverse-80ef2",
    'storageBucket': "ideaverse-80ef2.appspot.com",
    'messagingSenderId': "2138106869",
    'appId': "1:2138106869:web:b4652eda13b5009a850ebc",
    'measurementId': "G-VZRF1ZP2YJ",
    'databaseURL': "https://ideaverse-80ef2-default-rtdb.firebaseio.com/"
}
firebase = initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)

value = {
    'email': '',
    'password': '',
    'username': '',
    'confirm_pass': ''
}

@app.route("/")
def login_page():
    return render_template('login.html', value = value)

@app.route('/create_account', methods = ['POST'])
def create_account():
    value['email'] = email = request.form.get('email')
    value['username'] = username = request.form.get('username')
    value['password'] = password = request.form.get('password')
    value['confirm_pass'] = confirm_pass = request.form.get('confirm_pass')
    if len(password) < 8:
        return render_template('create_account.html',
                    error_message = 'Password should be greater than 8 characters',
                    value = value
                )

@app.route('/login', methods = ['POST'])
def login():
    value['email'] = email = request.form.get('email')
    value['password'] = password = request.form.get('password')

    user = ''
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return redirect(url_for('home_page'))
    except Exception as e:
        return render_template('login.html', error_message = 'Invalid email/password combination', value = value)
    
@app.route('/home')
def home_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)