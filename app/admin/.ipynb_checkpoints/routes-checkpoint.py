from flask import Blueprint, render_template, request, redirect, url_for
import pandas as pd
from app.extensions import mongo
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/import_csv")
@login_required
def import_csv():
    if current_user.role != "admin":
        return "Access denied"

    # path to CSV
    path = "app/static/data/stroke_data.csv"

    df = pd.read_csv(path)

    # Convert DataFrame to dictionary
    records = df.to_dict(orient="records")

    # Insert into MongoDB collection
    mongo.db.stroke_records.insert_many(records)

    return "CSV successfully imported into MongoDB!"