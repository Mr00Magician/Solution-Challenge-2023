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

categories = [
    'Healthcare', 
    'Technology', 
    'Education', 
    'Business or Entrepreneurship', 
    'Science and Research', 
    'E-Sports', 
    'Environmentalism',
    'Entertainment'
]

app = Flask(__name__, template_folder = '../front-end/templates', static_folder = '../front-end/static')

value = {
    'email': '',
    'password': '',
    'username': '',
    'confirm_pass': ''
}

class Refs:

    '''db_structure = {
        'users_info': {
            'total_users': 1, 
            'users': {
                'username': {
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
                    'name': 'nameless wonder',
                    'idea': 'idea1',
                    'members': {'MrMagician': 'MrMagician'}
                }
            }
        },
        'categories_info': {
            'Healthcare': {
                    'idea1': {'title': 'dummy title1'},
                    'idea2': {'title': 'dummy title2'}
            },
            'Technology': {
                    'idea3': {'title': 'dummy title3'},
                    'idea4': {'title': 'dummy title4'}
            }
        }
    }'''

    @staticmethod
    def get_idea(idea, token = None):
        return db.child('ideas_info').child('ideas').child(idea).get(token).val()
    @staticmethod
    def get_user(user, token = None):
        return db.child('users_info').child('users').child(user).get(token).val()
    @staticmethod
    def get_team(team, token = None):
        return db.child('teams_info').child('teams').child(team).get(token).val()

    @staticmethod
    def get_all_ideas(token = None):
        return Refs.get_idea('/', token)
    @staticmethod
    def get_all_users(token = None):
        return Refs.get_user('/', token)
    @staticmethod
    def get_all_teams(token = None):
        return Refs.get_team('/', token)

    @staticmethod
    def add_idea(idea, token = None):
        db.child('ideas_info').child('ideas').update(idea, token)
    @staticmethod
    def add_user(user, token = None):
        db.child('users_info').child('users').update(user, token)
    @staticmethod
    def add_team(team, token = None):
        db.child('teams_info').child('teams').update(team, token)

    @staticmethod
    def update_idea(idea, team_ID = None, title = None, description = None, token = None):
        idea_ref: pyrebase.pyrebase.Database = lambda: db.child('ideas_info').child('ideas').child(idea)
        if team_ID is not None:
            idea_ref.child('teams_working').update({team_ID: team_ID}, token)
        if title is not None:
            idea_ref.child('title').set(title, token)
        if description is not None:
            idea_ref.child('description').set(description, token)
    @staticmethod
    def update_team(team, name = None, new_member = None, token = None):
        team_ref: pyrebase.pyrebase.Database = lambda: db.child('teams_info').child('teams').child(team)
        if new_member is not None:
            team_ref.child('members').update({new_member: new_member}, token)
        if name is not None:
            team_ref.child('name').set(name, token)

    @staticmethod
    def get_tot_users(token = None):
        return db.child('users_info').child('total_users').get(token).val()
    @staticmethod
    def get_tot_ideas(token = None):
        return db.child('ideas_info').child('total_ideas').get(token).val()
    @staticmethod
    def get_tot_teams(token = None):
        return db.child('teams_info').child('total_teams').get(token).val()
    
    @staticmethod
    def set_tot_users(value, token = None):
        db.child('users_info').child('total_users').set(value, token)
    @staticmethod
    def set_tot_ideas(value, token = None):
        db.child('ideas_info').child('total_ideas').set(value, token)
    @staticmethod
    def set_tot_teams(value, token = None):
        db.child('teams_info').child('total_teams').set(value, token)

    @staticmethod
    def add_in_category(category, idea_ID_and_title, token = None):
        db.child('categories_info').child(category).update(idea_ID_and_title, token)
    @staticmethod
    def get_all_from(category, token = None):
        db.child('categories_info').child(category).child('/').get(token).val()

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
    
    if Refs.get_user(username) is not None:
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
        
        user = {
            username: {
                'email': email
            }
        }

        Refs.add_user(user, auth.current_user['idToken'])
        Refs.set_tot_users(Refs.get_tot_users() + 1)

        return redirect(url_for('home_page'))
    except Exception as e:
        return render_template('create_account_page', error_message = 'Some error occurred. Please try again.')

@app.route('/home')
def home_page():
    return render_template('index.html', user = auth.current_user)

@app.route('/home/ideasboard')
def ideasboard():
    idea = request.args.get('idea')
    if idea is None:
        idea = dict()
        idea['title'] = ''
        idea['description'] = ''
        idea['tags'] = ''
        idea['users'] = ''
        
    return render_template('ideasboard.html', user = auth.current_user, value = idea)

@app.route('/home/ideasboard/submit-idea', methods = ['POST'])
def submit_idea():
    # Checks Needed:
    # Check if condition for adding only existing users to the default team for this idea works.
    try:
        value = dict()
        value['title'] = request.json['title']
        value['description'] = request.json['description']
        value['tags'] = request.json['tags']
        value['users'] = request.json['users']
        value['team_name'] = request.json['team_name']

        for tag in value['tags']:
            if tag not in categories:
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = 'Invalid Tag choice!', idea =  value)),
                })
            
        for user in value['users']:
            if Refs.get_user(user) is None:
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = f'User "{user}" does not exist!', idea =  value)),
                })
        
        tot_teams = Refs.get_tot_teams()
        tot_ideas = Refs.get_tot_ideas()
        team_id = f'team{tot_teams + 1}'
        idea_id = f'idea{tot_ideas + 1}'

        team = {
            team_id: {
                'name': value['team_name'],
                'idea': idea_id,
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
        
        Refs.add_team(team)
        Refs.set_tot_teams(tot_teams + 1)
        Refs.add_idea(idea)
        Refs.set_tot_ideas(tot_ideas + 1)

        idea[idea_id] = {key: idea[idea_id][key] for key in idea[idea_id] if key == 'title'}
        for category in categories:
            Refs.add_in_category(category, idea)

    except Exception as e:
        return jsonify({
            'redirect_to': '{}'.format(url_for('idea_submission_result', message = 'An Error Occurred! Please try again.')),
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

@app.route('/home/explore-ideas')
def explore_ideas_page():
    return render_template (
        template_name_or_list = 'explore-ideas.html', categories = categories)

@app.route('/home/explore-ideas/<category>')
def ideas_from_category(category):
    if category not in categories:
        return '<h1 align = "center">Bad request!</h1>'
    ideas = Refs.get_all_from(category)
    # after receiving this on the front end, display the titles in a container and put the idea_id in a sub-container and set its display to none 
    return jsonify(ideas)

@app.route('/home/explore-ideas/<idea_ID>')
def get_idea_info(idea_ID):
    idea = Refs.get_idea(idea_ID)
    if idea is None:
        return '<h1 align = "center">Bad request!</h1>'
    return jsonify(idea)

@app.route('/home/explore-ideas/<idea_ID>/add-team/')
def add_team(idea_ID):
    team_info = dict()
    team_info['name'] = request.json['name']
    team_info['members'] = request.json['members']

    for member in value['members']:
        if Refs.get_user(member) is None:
            return jsonify({
                'error': 'yes',
                'message': f'User {member} does not exist!'
            })
    if Refs.get_idea(idea_ID) is None:
        return jsonify({
            'error': 'yes',
            'message': f'Idea does not exist!'
        })
    
    tot_teams = Refs.get_tot_teams()
    team_id = f'team{tot_teams + 1}'

    team = {
        team_id: {
            'name': value['team_name'],
            'idea': idea_ID,
            'members': {x: x for x in team_info['members']}
        }
    }

    Refs.add_team(team)
    Refs.set_tot_teams(tot_teams + 1)
    Refs.update_idea(idea_ID, team_id)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)