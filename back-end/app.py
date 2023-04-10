from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

firebase_config = eval(os.environ.get('FIREBASE_OPTIONS_CONFIG'))
firebase = pyrebase.initialize_app (firebase_config)

auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

categories = ['healthcare', 'technology']

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
            'username': {
                'username':'Mr_Magician', 
                'email':'meanasnadeem@gmail.com',
                'ideas_posted': {'idea1': 'idea1'}
            }
        }
    },
    'ideas_info': {
        'total_ideas': 0,
        'ideas': {
            'idea1': {
              'title':'dummy title',
              'description': 'sample description',
              'categories': [],
              'teams_working': {'team1': 'team1', 'team2': 'team2'}
            }
        }
    },
    'teams_info': {
        'total_teams': 0,
        'teams': {
            'team1': {
                'idea': 'idea1',
                'members': {'MrMagician': 'MrMagician'}
            }
        }
    },
    'categories_info': {
        'healthcare': {
            'total_ideas': 0,
            'ideas': {
                'idea1': 'idea1',
                'idea2': 'idea2
            }
        },
        'technology': {
            'total_ideas': 0,
            'ideas': {
                'idea3': 'idea3',
                'idea4': 'idea4'
            }
        }
    }
}'''

@app.route("/")
def login_page():
    error_message = request.args.get('error_message')
    if error_message is None:
        error_message = ''
    return render_template('login.html', value = value, error_message = error_message)

@app.route('/login', methods = ['POST'])
def login():
    value['email'] = email = request.form.get('email')
    value['password'] = password = request.form.get('password')

    try:
        auth.sign_in_with_email_and_password(email, password)
        return redirect(url_for('home_page'))
    except Exception as e:
        return redirect(url_for('login_page', error_message = 'Invalid email/password combination'))

@app.route('/create-account')
def create_account_page():
    error_message = request.args.get('error_message')
    if error_message is None:
        error_message = ''
    return render_template('create-account.html', value = value, error_message = error_message)

@app.route('/create-account/sign-up', methods = ['POST'])
def create_account():
    value['email'] = email = request.form.get('email') 
    value['username'] = username = request.form.get('username')
    value['password'] = password = request.form.get('password')
    value['confirm_pass'] = confirm_pass = request.form.get('confirm_pass')
    
    if db.child('users_info').child('users').child(username).get().val() is not None:
        return redirect(url_for('create_account_page', error_message = 'Username already exists'))

    if len(password) < 8:
        return redirect(url_for('create_account_page', error_message = 'Password should be greater than 8 characters'))
    
    if len(password) > 30:
        return redirect(url_for('create_account_page', error_message = 'Password should not be more than 30 characters'))
    
    if password != confirm_pass:
        return redirect(url_for('create_account_page', error_message = 'Passwords do not match!'))

    try:
        auth.create_user_with_email_and_password(email, password)
    except Exception as e:
        return render_template('create_account_page', error_message = 'Email already exists')
    try: 
        auth.sign_in_with_email_and_password(email, password)
        auth.update_profile(auth.current_user['idToken'], display_name=username, photo_url = storage.child('no-profile-image.png').get_url(None))
        
        db.child('users_info').child('users').child(username).set({'username':username, 'email':email}, auth.current_user['idToken'])
        tot_users = db.child('users_info').child('total_users').get().val()
        db.child('users_info').child('total_users').set(tot_users + 1, auth.current_user['idToken'])

        return redirect(url_for('home_page'))
    except Exception as e:
        return render_template('create_account_page', error_message = 'Some error occurred. Please try again.')

@app.route('/home')
def home_page():
    return render_template('index.html', user = auth.current_user)

@app.route('/home/ideasboard')
def ideasboard():
    idea = request.args.get('idea')
    return render_template('ideasboard.html', user = auth.current_user, value = idea)

@app.route('/home/ideasboard/submit-idea', methods = ['POST'])
def submit_idea():
    try:
        value = dict()
        value['title'] = request.json['title']
        value['description'] = request.json['description']
        value['tags'] = request.json['tags']
        value['users'] = request.json['users']

        for tag in value['tags']:
            if tag not in categories:
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = 'Invalid Tag choice!', value = value)),
                })
            
        for user in value['users']:
            if user not in db.child('users_info').child('users').get().val().keys():
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = f'User "{user}" does not exist!', value = value)),
                })
        
        tot_teams = db.child('teams_info').child('total_teams').get().val()
        tot_ideas = db.child('ideas_info').child('total_ideas').get().val()
        team_id = f'team{tot_teams + 1}'
        idea_id = f'idea{tot_ideas + 1}'

        team = {
            team_id: {
                'idea': f'idea{tot_ideas + 1}',
                'members': {x: x for x in value['users']}
            }
        }
        idea = {
            idea_id: {
                'title': value['title'],
                'description': value['description'],
                'categories': value['tags'],
                'teams_working': {team_id: team_id}
            }
        }

        db.child('teams_info').child('teams').update(team)
        db.child('teams_info').child('total_teams').set(tot_teams + 1)
        db.child('ideas_info').child('ideas').update(idea)
        db.child('ideas_info').child('total_ideas').set(tot_ideas + 1)

    except Exception as e:
        return jsonify({
            'redirect_to': '{}'.format(url_for('idea_submission_result', message = 'An Error Occurred!', value = value)),
        })
    
    return jsonify({
            'redirect_to': '{}'.format(url_for('idea_submission_result', message = 'Idea Submitted Successfully!')),
        })

@app.route('/home/ideasboard/submit-idea/result')
def idea_submission_result():
    message = request.args.get('message')
    idea = request.args.get('idea')
    # return render_template('idea-submission-result.html', message = message)
    return f'<h1> message = {message} {idea} </h1>'

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)