import os
import logging
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV_TYPE = os.environ.get('ENV_TYPE')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_ATLAS_URI = os.environ.get('DB_ATLAS_URI')
    # Path for storing profile pictures
    PROFILE_PICS_PATH = os.path.join(basedir, 'app', 'static', 'profile_pics')
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    MICROSOFT_AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('TENANT_ID', 'common')}"
    MICROSOFT_REDIRECT_PATH = '/auth/callback'  # Redirect URI path
    MICROSOFT_SCOPES = ["User.ReadBasic.All"]  # Permissions to request from Microsoft
    ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set!")
    if not DB_USERNAME or not DB_PASSWORD:
        raise ValueError("Database credentials are missing!")
    
    
logging.basicConfig(level=logging.INFO)
logging.info(f"Config loaded: {basedir}")