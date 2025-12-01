from flask import Blueprint, render_template
from flask_login import login_required

doctor_bp = Blueprint("doctor", __name__, template_folder="../templates" , url_prefix="/doctor")

@doctor_bp.route("/")
@login_required
def dashboard():
    return render_template("doctor/dashboard.html")