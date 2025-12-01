from flask import Blueprint, render_template
from flask_login import login_required

nurse_bp = Blueprint("nurse", __name__,template_folder="../templates" , url_prefix="/nurse")

@nurse_bp.route("/")
@login_required
def dashboard():
    return render_template("nurse_dashboard.html")