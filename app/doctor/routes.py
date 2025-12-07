from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db, mongo
from app.models import User

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'doctor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Try to get patients from MongoDB, fallback to empty list
    try:
        patients = list(mongo.db.patients.find()) if mongo.db else []
    except:
        patients = []
    
    # Get statistics
    total_patients = len(patients)
    pending_appointments = 0  # Placeholder
    completed_appointments = 0  # Placeholder
    
    return render_template('doctor/dashboard.html',
                         patients=patients,
                         total_patients=total_patients,
                         pending_appointments=pending_appointments,
                         completed_appointments=completed_appointments)

@doctor_bp.route('/patients')
@login_required
def patients():
    if current_user.role.name != 'doctor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        patients = list(mongo.db.patients.find()) if mongo.db else []
    except:
        patients = []
    
    return render_template('doctor/patients.html', patients=patients)

@doctor_bp.route('/appointments')
@login_required
def appointments():
    if current_user.role.name != 'doctor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        appointments = list(mongo.db.appointments.find({'doctor_id': str(current_user.id)})) if mongo.db else []
    except:
        appointments = []
    
    return render_template('doctor/appointments.html', appointments=appointments)

@doctor_bp.route('/profile')
@login_required
def profile():
    if current_user.role.name != 'doctor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('doctor/profile.html', doctor=current_user)