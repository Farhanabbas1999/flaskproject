from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db, mongo
from app.models import User

nurse_bp = Blueprint('nurse', __name__)

@nurse_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Try to get patients from MongoDB, fallback to empty list
    try:
        patients = list(mongo.db.patients.find()) if mongo.db else []
    except:
        patients = []
    
    # Get statistics
    total_patients = len(patients)
    pending_tasks = 0
    completed_tasks = 0
    
    return render_template('nurse/dashboard.html',
                         patients=patients,
                         total_patients=total_patients,
                         pending_tasks=pending_tasks,
                         completed_tasks=completed_tasks)

@nurse_bp.route('/patients')
@login_required
def patients():
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        patients = list(mongo.db.patients.find()) if mongo.db else []
    except:
        patients = []
    
    return render_template('nurse/patients.html', patients=patients)

@nurse_bp.route('/patient/<patient_id>')
@login_required
def patient_detail(patient_id):
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    patient = mongo.db.patients.find_one({'_id': ObjectId(patient_id)})
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('nurse.patients'))
    
    return render_template('nurse/patient_detail.html', patient=patient)

@nurse_bp.route('/patient/<patient_id>/add-vitals', methods=['POST'])
@login_required
def add_vitals(patient_id):
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    blood_pressure = request.form.get('blood_pressure')
    heart_rate = request.form.get('heart_rate')
    temperature = request.form.get('temperature')
    oxygen_saturation = request.form.get('oxygen_saturation')
    
    mongo.db.patients.update_one(
        {'_id': ObjectId(patient_id)},
        {'$push': {
            'vitals': {
                'date': datetime.datetime.utcnow(),
                'recorded_by': current_user.username,
                'blood_pressure': blood_pressure,
                'heart_rate': heart_rate,
                'temperature': temperature,
                'oxygen_saturation': oxygen_saturation
            }
        }}
    )
    
    flash('Vitals recorded successfully', 'success')
    return redirect(url_for('nurse.patient_detail', patient_id=patient_id))

@nurse_bp.route('/patient/<patient_id>/add-note', methods=['POST'])
@login_required
def add_note(patient_id):
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    note = request.form.get('note')
    note_type = request.form.get('note_type', 'observation')
    
    mongo.db.patients.update_one(
        {'_id': ObjectId(patient_id)},
        {'$push': {
            'nurse_notes': {
                'date': datetime.datetime.utcnow(),
                'nurse': current_user.username,
                'type': note_type,
                'note': note
            }
        }}
    )
    
    flash('Note added successfully', 'success')
    return redirect(url_for('nurse.patient_detail', patient_id=patient_id))

@nurse_bp.route('/appointments')
@login_required
def appointments():
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Mock appointments - replace with real DB later
    appointments_list = [
        {'id': 1, 'patient': 'John Doe', 'doctor': 'Dr. Smith', 'date': '2025-12-08', 'time': '10:00 AM', 'status': 'confirmed'},
        {'id': 2, 'patient': 'Jane Smith', 'doctor': 'Dr. Johnson', 'date': '2025-12-08', 'time': '11:30 AM', 'status': 'pending'},
    ]
    
    return render_template('nurse/appointments.html', appointments=appointments_list)

@nurse_bp.route('/tasks')
@login_required
def tasks():
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        tasks = list(mongo.db.nurse_tasks.find({'nurse_id': str(current_user.id)})) if mongo.db else []
    except:
        tasks = []
    
    return render_template('nurse/tasks.html', tasks=tasks)

@nurse_bp.route('/profile')
@login_required
def profile():
    if current_user.role.name != 'nurse':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('nurse/profile.html', nurse=current_user)