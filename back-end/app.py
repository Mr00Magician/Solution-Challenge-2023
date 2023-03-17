from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

users = {
    'anas':'12345',
    'maaz':'54321'
}

value = {
    'username': '',
    'password': ''
}

@app.route("/")
def login_page():
    return render_template('login.html', value = value)

@app.route('/login', methods = ['POST'])
def login():
    value['username'] = username = request.form.get('username')
    value['password'] = password = request.form.get('password')
    try:
        if users[username] == password:
            return redirect(url_for('home_page'))
        else:
            return render_template('login.html', error_message = 'Invalid Password', value = value)
    except Exception as e:
        return render_template('login.html', error_message = 'Invalid Username', value = value)
    
@app.route('/home')
def home_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)