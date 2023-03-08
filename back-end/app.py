from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template('index.html')

@app.route('/ideasboard.html')
def ideasboard():
    return render_template('ideasboard.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)