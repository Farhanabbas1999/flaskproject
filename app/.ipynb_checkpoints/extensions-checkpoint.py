from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pymongo import PyMongo

db = SQLAlchemy()
login_manager = LoginManager()
mongo = PyMongo()