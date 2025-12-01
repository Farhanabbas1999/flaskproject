from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from app.models import User

patient_bp = Blueprint("patient", __name__, template_folder="../templates")

@patient_bp.route("/patient/login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"], role="patient").first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect("/patient/dashboard")
        return "Invalid Patient Login"
    
    return render_template("patient_login.html")