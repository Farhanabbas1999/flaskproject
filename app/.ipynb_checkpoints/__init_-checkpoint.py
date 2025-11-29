from flask import Flask
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(_name_)

    # creating a Seceret key
    app.config["SECRET_KEY"] = "Farhan1234"
    csrf.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app