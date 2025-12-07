from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db, mongo
from app.models import User

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'patient':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Try to get patient data from MongoDB, fallback to None
    try:
        patient = mongo.db.patients.find_one({'user_id': current_user.id}) if mongo.db else None
    except:
        patient = None
    
    # Get statistics
    total_appointments = 0
    pending_tests = 0
    recent_visits = []
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         total_appointments=total_appointments,
                         pending_tests=pending_tests,
                         recent_visits=recent_visits)

@patient_bp.route('/profile')
@login_required
def profile():
    if current_user.role.name != 'patient':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        patient = mongo.db.patients.find_one({'user_id': current_user.id}) if mongo.db else None
    except:
        patient = None
    
    return render_template('patient/profile.html', patient=patient)

@patient_bp.route('/appointments')
@login_required
def appointments():
    if current_user.role.name != 'patient':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        appointments = list(mongo.db.appointments.find({'patient_id': current_user.id})) if mongo.db else []
    except:
        appointments = []
    
    return render_template('patient/appointments.html', appointments=appointments)

@patient_bp.route('/medical-records')
@login_required
def medical_records():
    if current_user.role.name != 'patient':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        records = list(mongo.db.medical_records.find({'patient_id': current_user.id})) if mongo.db else []
    except:
        records = []
    
    return render_template('patient/medical_records.html', records=records)

@patient_bp.route('/stroke-assessment', methods=['GET', 'POST'])
@login_required
def stroke_assessment():
    if current_user.role.name != 'patient':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        age = request.form.get('age')
        gender = request.form.get('gender')
        hypertension = request.form.get('hypertension')
        heart_disease = request.form.get('heart_disease')
        smoking_status = request.form.get('smoking_status')
        bmi = request.form.get('bmi')
        glucose_level = request.form.get('glucose_level')
        
        # TODO: Implement stroke risk prediction model
        # For now, just save the data
        
        try:
            if mongo.db:
                assessment_data = {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'age': age,
                    'gender': gender,
                    'hypertension': hypertension,
                    'heart_disease': heart_disease,
                    'smoking_status': smoking_status,
                    'bmi': bmi,
                    'glucose_level': glucose_level,
                    'timestamp': datetime.utcnow()
                }
                mongo.db.stroke_assessments.insert_one(assessment_data)
                flash('Stroke assessment submitted successfully!', 'success')
            else:
                flash('Assessment service temporarily unavailable.', 'warning')
        except:
            flash('Error submitting assessment. Please try again.', 'danger')
        
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/stroke_assessment.html')