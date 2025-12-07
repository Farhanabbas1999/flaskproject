from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db, mongo, csrf
from app.models import User, Role
from app.admin.analytics import get_stroke_analytics
from app.utils import admin_required
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_doctors = User.query.join(Role).filter(Role.name == 'doctor').count()
    total_patients = User.query.join(Role).filter(Role.name == 'patient').count()
    total_nurses = User.query.join(Role).filter(Role.name == 'nurse').count()
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_nurses': total_nurses,
        'pending_approvals': pending_approvals,
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users)

@admin_bp.route('/pending-approvals')
@login_required
@admin_required
def pending_approvals():
    pending_users = User.query.filter_by(is_approved=False).order_by(User.created_at.desc()).all()
    pending_approvals = len(pending_users)
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/pending_approvals.html', 
                         pending_users=pending_users, 
                         stats=stats)

@admin_bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.username} has been approved!', 'success')
    return redirect(url_for('admin.pending_approvals'))

@admin_bp.route('/reject-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been rejected and removed.', 'success')
    return redirect(url_for('admin.pending_approvals'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/users.html', users=all_users, stats=stats)

@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    doctor_role = Role.query.filter_by(name='doctor').first()
    doctors = User.query.filter_by(role_id=doctor_role.id).all() if doctor_role else []
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/doctors.html', doctors=doctors, stats=stats)

@admin_bp.route('/nurses')
@login_required
@admin_required
def nurses():
    nurse_role = Role.query.filter_by(name='nurse').first()
    nurses = User.query.filter_by(role_id=nurse_role.id).all() if nurse_role else []
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/nurses.html', nurses=nurses, stats=stats)

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    try:
        patients = list(mongo.db.patients.find()) if mongo.db else []
    except:
        patients = []
    
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/patients.html', patients=patients, stats=stats)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    analytics_data = get_stroke_analytics()
    
    stats = {
        'total_dataset_records': analytics_data.get('total_records', 0),
        'stroke_cases': analytics_data.get('stroke_cases', 0),
        'total_patients': mongo.db.patients.count_documents({}) if mongo.db else 0,
        'total_users': User.query.count()
    }
    
    return render_template('admin/analytics.html', 
                         stats=stats,
                         gender_data=json.dumps(analytics_data.get('gender_stats', {})),
                         age_data=json.dumps(analytics_data.get('age_stats', {})),
                         hypertension_data=json.dumps(analytics_data.get('hypertension_stats', {})),
                         heart_disease_data=json.dumps(analytics_data.get('heart_disease_stats', {})),
                         work_type_data=json.dumps(analytics_data.get('work_type_data', {})),  # CHANGED
                         bmi_stroke_data=json.dumps(analytics_data.get('bmi_stroke_data', {})),
                         glucose_stroke_data=json.dumps(analytics_data.get('glucose_stroke_data', {})))

@admin_bp.route('/manage-admins')
@login_required
@admin_required
def manage_admins():
    admin_role = Role.query.filter_by(name='admin').first()
    admins = User.query.filter_by(role_id=admin_role.id).all() if admin_role else []
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    stats = {
        'pending_approvals': pending_approvals
    }
    
    return render_template('admin/manage_admins.html', admins=admins, stats=stats)

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
@csrf.exempt
def create_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Get admin role
        admin_role = Role.query.filter_by(name='admin').first()
        
        # Create new admin
        new_admin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role_id=admin_role.id,
            is_active=True,
            is_approved=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash(f'Admin account "{username}" created successfully!', 'success')
        return redirect(url_for('admin.manage_admins'))
    
    return render_template('admin/create_admin.html')

@admin_bp.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted!', 'success')
    return redirect(url_for('admin.users'))