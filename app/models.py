from app import login, db, USERS
from flask_login import UserMixin
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger("pm-tool")

class User:
    def __init__(self, id):
        try:
            u = USERS.find_one({"_id": ObjectId(id)})
            if not u:
                raise ValueError("User not found")
            self.id = id
            self.name = u["name"]
            self.email = u["email"]
            self.profile_pic = u.get("profile_pic", None)
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            raise RuntimeError(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error initializing user: {e}")
            raise ValueError(f"Error loading user: {e}")

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
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_pic": self.profile_pic
        }
        
    @staticmethod
    def find_by_email(email):
        return USERS.find_one({"email": email})


    @login.user_loader
    def load_user(id):
        try:
            u = USERS.find_one({"_id": ObjectId(id)})
            if not u:
                logger.warning(f"User not found: {id}")
                return None
            return User(id=str(u['_id']))
        except Exception as e:
            logger.error(f"Error loading user: {e}")
            return None