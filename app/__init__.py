from flask import Flask
from flask_wtf import CSRFProtect
from config import Config
from flask_login import LoginManager
from pymongo import MongoClient
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Login required!'
login.login_message_category = 'alert-warning'
bootstrap = Bootstrap5(app)
client = MongoClient('localhost', 27017) # username=app.config['DB_USERNAME'], password=app.config['DB_PASSWORD']
db = client["pm-tool"]
PROJECTS = db["projects"]
TASKS = db["tasks"]
USERS = db["users"]
USER_PROJECTS = db["user_projects"]

from app import routes