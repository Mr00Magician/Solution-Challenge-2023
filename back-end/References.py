import pyrebase
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

    def __init__(self, db) -> None:
        self.db: pyrebase.pyrebase.Database = db
 
    def get_idea(self, idea, token = None):
        return self.db.child('ideas_info').child('ideas').child(idea).get(token).val()
    
    def get_user(self, user, token = None):
        return self.db.child('users_info').child('users').child(user).get(token).val()
    
    def get_team(self, team, token = None):
        return self.db.child('teams_info').child('teams').child(team).get(token).val()

    
    def get_all_ideas(self, token = None):
        return Refs.get_idea('/', token)
    
    def get_all_users(self, token = None):
        return Refs.get_user('/', token)
    
    def get_all_teams(self, token = None):
        return Refs.get_team('/', token)

    
    def add_idea(self, idea, token = None):
        self.db.child('ideas_info').child('ideas').update(idea, token)
    
    def add_user(self, user, token = None):
        self.db.child('users_info').child('users').update(user, token)
    
    def add_team(self, team, token = None):
        self.db.child('teams_info').child('teams').update(team, token)

    
    def update_idea(self, idea, team_ID = None, title = None, description = None, token = None):
        idea_ref: pyrebase.pyrebase.Database = lambda: self.db.child('ideas_info').child('ideas').child(idea)
        if team_ID is not None:
            idea_ref.child('teams_working').update({team_ID: team_ID}, token)
        if title is not None:
            idea_ref.child('title').set(title, token)
        if description is not None:
            idea_ref.child('description').set(description, token)
    
    def update_team(self, team, name = None, new_members = None, token = None):
        team_ref: pyrebase.pyrebase.Database = lambda: self.db.child('teams_info').child('teams').child(team)
        if new_members is not None:
            team_ref.child('members').update({new_member: new_member for new_member in new_members}, token)
        if name is not None:
            team_ref.child('name').set(name, token)

    
    def get_tot_users(self, token = None):
        return self.db.child('users_info').child('total_users').get(token).val()
    
    def get_tot_ideas(self, token = None):
        return self.db.child('ideas_info').child('total_ideas').get(token).val()
    
    def get_tot_teams(self, token = None):
        return self.db.child('teams_info').child('total_teams').get(token).val()
    
    
    def set_tot_users(self, value, token = None):
        self.db.child('users_info').child('total_users').set(value, token)
    
    def set_tot_ideas(self, value, token = None):
        self.db.child('ideas_info').child('total_ideas').set(value, token)
    
    def set_tot_teams(self, value, token = None):
        self.db.child('teams_info').child('total_teams').set(value, token)

    
    def add_in_category(self, category, idea_ID_and_title, token = None):
        self.db.child('categories_info').child(category).update(idea_ID_and_title, token)
    
    def get_all_from(self, category, token = None):
        self.db.child('categories_info').child(category).child('/').get(token).val()