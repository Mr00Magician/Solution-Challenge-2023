from flask import Flask, render_template, request

app = Flask(__name__)

users = {
    'anas':'12345',
    'maaz':'54321'
}

@app.route("/")
def home_page():
    return render_template('login.html')

@app.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    try:
        if users[username] == password:
            return render_template('index.html')
        else:
            return '<h1>Wrong Password</h1>'
    except:
        return '<h1>Username does not exist</h1>'

# @app.route('/ideasboard.html')
# def ideasboard():
#     return render_template('ideasboard.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)