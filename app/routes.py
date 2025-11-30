from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db

bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return "Flask app working successfully!"

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now login.")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


import pandas as pd
from .models import StrokeRecord, db
from flask_login import login_required

@bp.route("/import_csv")
@login_required
def import_csv():
    df = pd.read_csv("healthcare-dataset-stroke-data.csv")

    for _, row in df.iterrows():
        record = StrokeRecord(
            gender=row["gender"],
            age=row["age"],
            hypertension=row["hypertension"],
            heart_disease=row["heart_disease"],
            ever_married=row["ever_married"],
            work_type=row["work_type"],
            Residence_type=row["Residence_type"],
            avg_glucose_level=row["avg_glucose_level"],
            bmi=row["bmi"],
            smoking_status=row["smoking_status"],
            stroke=row["stroke"]
        )
        db.session.add(record)

    db.session.commit()
    return "CSV imported successfully!"
@bp.route("/records")
@login_required
def view_records():
    records = StrokeRecord.query.limit(20).all()
    return render_template("records.html", records=records)



@bp.route("/create_admin")
def create_admin():
    from .models import User
    from app import db
    user = User(username="admin", password="admin123")
    db.session.add(user)
    db.session.commit()
    return "Admin user created!"