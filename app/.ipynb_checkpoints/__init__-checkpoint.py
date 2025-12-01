from flask import Flask
from .extensions import db, login_manager, mongo
from .models import User



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    # MONGO DB
    app.config["MONGO_URI"] = "mongodb://localhost:27017/hospital_db"

    # INIT EXTENSIONS
    db.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)

    # LOGIN MANAGER
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # BLUEPRINT REGISTRATION (ADDS URL PREFIXES)
    from .auth.routes import auth_bp
    from .patient.routes import patient_bp
    from .doctor.routes import doctor_bp
    from .nurse.routes import nurse_bp
    from .admin.routes import admin_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(patient_bp, url_prefix="/patient")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(nurse_bp, url_prefix="/nurse")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(main_bp)

    # CREATE SQLITE TABLES
    with app.app_context():
        db.create_all()

    return app