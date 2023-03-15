from flask import Flask, render_template, request, jsonify, url_for, redirect

app = Flask(__name__)

users = {
    'anas':'12345',
    'maaz':'54321'
}

@app.route("/")
def home_page():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    # print(request.form)
    return jsonify(request.form)
    try:
        if users[username] == password:
            return render_template('index.html')
        else:
            return render_template('login.html', error_message = 'Invalid Password')
    except:
        return render_template('login.html', error_message = 'Invalid Username')

# @app.route('/ideasboard.html')
# def ideasboard():
#     return render_template('ideasboard.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)