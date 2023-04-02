from flask import Flask, render_template, request, redirect, url_for, jsonify
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
storage = firebase.storage()

app = Flask(__name__, template_folder = '../front-end/templates', static_folder = '../front-end/static')

value = {
    'email': '',
    'password': '',
    'username': '',
    'confirm_pass': ''
}

'''db_structure = {
    'users_info': {
        'total_users': 1, 
        'users': {
            'Mr_Magician': {
                'username':'Mr_Magician', 
                'email':'meanasnadeem@gmail.com',
                # 'ideas_posted': {'idea1': 'idea1'}
            }
        }
    },
    'ideas_info': {
        'total_ideas': 0,
    #     'ideas': {
    #         'idea1': {
    #           'serial':1,
    #           'title':'dummy title',
    #           'description': 'sample description',
    #           'teams_working': {'team1': 'team1', 'team2': 'team2'}
    #         }
    #     }
    },
    'teams_info': {
        'total_teams': 0,
        # 'teams': {
        #     'team1': {
        #         'serial': 1,
        #         'idea_serial': 1,
        #         'members': {'MrMagician': 'MrMagician'}
        #     }
        # }
    }
}'''

current_user = ''

@app.route("/")
def login_page():
    return render_template('login.html', value = value)

@app.route('/create-account')
def create_account_page():
    return render_template('create-account.html', value = value)

@app.route('/create-account/sign-up', methods = ['POST'])
def create_account():
    global current_user

    value['email'] = email = request.form.get('email') 
    value['username'] = username = request.form.get('username')
    value['password'] = password = request.form.get('password')
    value['confirm_pass'] = confirm_pass = request.form.get('confirm_pass')
    
    if db.child('users_info').child('users').child(username).get().val() is not None:
        return render_template('create-account.html',
                    error_message = 'Username already exists',
                    value = value
                )

    if len(password) < 8:
        return render_template('create-account.html',
                    error_message = 'Password should be greater than 8 characters',
                    value = value
                )
    
    if len(password) > 30:
        return render_template('create-account.html',
                    error_message = 'Password should not be more than 30 characters',
                    value = value
                )
    
    current_user = auth.create_user_with_email_and_password(email, password)
    current_user['displayName'] = username
    auth.update_profile(current_user['idToken'], display_name=username, photo_url = storage.child('no-profile-image.png').get_url(None))
    
    db.child('users_info').child('users').child(username).set({'username':username, 'email':email})
    tot_users = db.child('users_info').child('total_users').get().val()
    db.child('users_info').child('total_users').set(tot_users + 1)

    return redirect(url_for('home_page'))

@app.route('/login', methods = ['POST'])
def login():
    global current_user
    
    value['email'] = email = request.form.get('email')
    value['password'] = password = request.form.get('password')

    try:
        current_user = auth.sign_in_with_email_and_password(email, password)
        return redirect(url_for('home_page'))
    except Exception as e:
        # change this to redirect
        return render_template('login.html', error_message = 'Invalid email/password combination', value = value)
    
@app.route('/home')
def home_page():
    # print(current_user)
    return render_template('index.html', user = current_user)

@app.route('/home/ideasboard')
def ideasboard():
    return render_template('ideasboard.html', user = current_user)

@app.route('/home/ideasboard/submit-idea', methods = ['POST'])
def submit_idea():
    # print(request.json)
    title = request.json['title']
    description = request.json['description']
    
    return jsonify(request.json)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)