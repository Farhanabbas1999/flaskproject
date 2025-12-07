from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mongo = PyMongo()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'  # Add this line
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'Session expired, please log in again.'
login_manager.needs_refresh_message_category = 'info'