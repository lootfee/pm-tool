from app import login, db, USERS
from flask_login import UserMixin
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, id):
        u = USERS.find_one({"_id": ObjectId(id)})
        self.id = id
        self.name = u["name"]
        self.email = u["email"]

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id
    
    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)


    @login.user_loader
    def load_user(id):
        u = USERS.find_one({"_id": ObjectId(id)})
        if not u:
            return None
        return User(id=str(u['_id']))