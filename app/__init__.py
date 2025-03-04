import os
import logging
from flask import Flask
from flask_wtf import CSRFProtect
from config import Config
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_bootstrap import Bootstrap5
from msal import ConfidentialClientApplication
from werkzeug.middleware.profiler import ProfilerMiddleware

# initialize app and logging
app = Flask(__name__)
app.config.from_object(Config)
logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger("pm-tool")

# Ensure the PROFILE_PICS_PATH exists
profile_pics_path = app.config["PROFILE_PICS_PATH"]
if not os.path.exists(profile_pics_path):
    os.makedirs(profile_pics_path)
    print(f"Created directory: {profile_pics_path}")

# Flask extensions
csrf = CSRFProtect(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Login required!'
login.login_message_category = 'alert-warning'
bootstrap = Bootstrap5(app)

# Database connection
try:
    if app.config.get('ENV_TYPE') == 'production':
        client = MongoClient(app.config.get('DB_ATLAS_URI'), server_api=ServerApi('1'))
    else:
        client = MongoClient(
            host=app.config.get('DB_HOST'),
            port=int(app.config.get('DB_PORT')),
            username=app.config.get('DB_USERNAME'),
            password=app.config.get('DB_PASSWORD')
        )
    db = client["pm-tool"]
    PROJECTS = db["projects"]
    TASKS = db["tasks"]
    USERS = db["users"]
    USER_PROJECTS = db["user_projects"]
    PROJECT_INVITES = db['project_invites']
    NOTIFICATIONS = db['notifications']
    PROJECT_LOGS = db['project_logs']
except Exception as e:
    app.logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Microsoft OAuth
try:
    msal_app = ConfidentialClientApplication(
        app.config["MICROSOFT_CLIENT_ID"],
        authority=app.config["MICROSOFT_AUTHORITY"],
        client_credential=app.config["MICROSOFT_CLIENT_SECRET"]
    )
except Exception as e:
    msal_app = None
    app.logger.error("Microsoft authentication initialization failed!")
    

from app import routes