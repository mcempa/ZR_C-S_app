from config import ROLE_PERMISSIONS


class User():
    def __init__(self):
        self.id = None  
        self.username = None
        self.password = None
        self.role = 'user'
        self.is_logged = False
        self.login_time = None
        self.create_time = None

    def is_user_allowed_to_command(self, command):
        permissions = ROLE_PERMISSIONS[self.role][command]
        return permissions
