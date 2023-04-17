from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyrebase
import os
from dotenv import load_dotenv
from References import Refs

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

refs = Refs(db)

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
    
    if refs.get_user(username) is not None:
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

        refs.add_user(user, auth.current_user['idToken'])
        refs.set_tot_users(refs.get_tot_users() + 1)

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
        value['users'] = request.json['teamMembers']
        value['team_name'] = request.json['team_name']

        for tag in value['tags']:
            if tag not in categories:
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = 'Invalid Tag choice!', idea =  value)),
                })
            
        for user in value['users']:
            if refs.get_user(user) is None:
                return jsonify({
                    'redirect_to': '{}'.format(url_for('ideasboard', error_message = f'User "{user}" does not exist!', idea =  value)),
                })
        
        tot_teams = refs.get_tot_teams()
        tot_ideas = refs.get_tot_ideas()
        team_id = f'team{tot_teams + 1}'
        idea_id = f'idea{tot_ideas + 1}'

        team = {
            team_id: {
                'name': value['team_name'],
                'team_leader': auth.current_user['displayName'],
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
        
        refs.add_team(team)
        refs.set_tot_teams(tot_teams + 1)
        refs.add_idea(idea)
        refs.set_tot_ideas(tot_ideas + 1)

        idea[idea_id] = {key: idea[idea_id][key] for key in idea[idea_id] if key == 'title'}
        for category in categories:
            refs.add_in_category(category, idea)

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
    # return render_template('idea-submission-result.html', message = message)
    return f'<h1> message = {message}</h1>'

@app.route('/home/explore-ideas')
def explore_ideas_page():
    return render_template (
        template_name_or_list = 'explore-ideas.html', categories = categories)

@app.route('/home/explore-ideas/<category>')
def ideas_from_category(category):
    if category not in categories:
        return '<h1 align = "center">Bad request!</h1>'
    ideas = refs.get_all_from(category)
    # after receiving this on the front end, display the titles in a container and put the idea_id in a sub-container and set its display to none 
    return jsonify(ideas)

@app.route('/home/explore-ideas/<idea_ID>')
def get_idea_info(idea_ID):
    idea = refs.get_idea(idea_ID)
    if idea is None:
        return '<h1 align = "center">Bad request!</h1>'
    return jsonify(idea)

@app.route('/home/explore-ideas/<idea_ID>/add-team/')
def add_team(idea_ID):
    team_info = dict()
    team_info['name'] = request.json['name']
    team_info['members'] = request.json['members']

    for member in value['members']:
        if refs.get_user(member) is None:
            return jsonify({
                'error': 'yes',
                'message': f'User {member} does not exist!'
            })
    if refs.get_idea(idea_ID) is None:
        return jsonify({
            'error': 'yes',
            'message': f'Idea does not exist!'
        })
    
    tot_teams = refs.get_tot_teams()
    team_id = f'team{tot_teams + 1}'

    team = {
        team_id: {
            'name': value['team_name'],
            'idea': idea_ID,
            'members': {x: x for x in team_info['members']}
        }
    }

    refs.add_team(team)
    refs.set_tot_teams(tot_teams + 1)
    refs.update_idea(idea_ID, team_id)

@app.route('/home/explore-ideas/<team_ID>/add-members')
def add_members(team_ID):
    try:
        new_members = request.json['new_members']

        for member in new_members:
            if refs.get_user(member) is None:
                return jsonify({
                    'error': 'yes',
                    'message': f'user {member} does not exist!'
                })
        if refs.get_team(team_ID) is None:
            return jsonify({
                'error': 'yes',
                'message': 'Invalid team ID!'
            })
        
        refs.update_team(team_ID, new_members = new_members)
    except Exception as e:
        return jsonify({
            'error': 'yes',
            'message': 'An unexpected error occurred!Please try again.'
        })
    
    return jsonify({
        'error': 'no',
        'message': 'Members successfully added to team!'
    })
    
if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)