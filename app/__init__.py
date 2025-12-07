from flask import Flask
from app.extensions import db, login_manager, mongo, csrf
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.doctor.routes import doctor_bp
    from app.nurse.routes import nurse_bp
    from app.patient.routes import patient_bp
    from app.main.routes import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(nurse_bp, url_prefix='/nurse')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(main_bp)
    
    # User loader
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
        init_roles()
    
    return app

def init_roles():
    """Initialize roles if they don't exist"""
    from app.models import Role
    
    roles = ['admin', 'doctor', 'nurse', 'patient']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name, description=f'{role_name.title()} role')
            db.session.add(new_role)
    
    db.session.commit()