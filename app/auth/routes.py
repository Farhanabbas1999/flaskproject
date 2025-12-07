from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Role
from app.extensions import db, csrf

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_name = request.form.get('role')
        
        # Prevent admin registration through normal form
        if role_name == 'admin':
            flash('Invalid role selection. Admin accounts must be created by system administrators.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Only allow: patient, doctor, nurse
        if role_name not in ['patient', 'doctor', 'nurse']:
            flash('Invalid role selection.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash('Invalid role', 'danger')
            return redirect(url_for('auth.register'))
        
        # Auto-approve patients, but require approval for doctors and nurses
        is_approved = (role_name == 'patient')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role_id=role.id,
            is_approved=is_approved
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        if is_approved:
            flash('Registration successful! Please login.', 'success')
        else:
            flash('Registration successful! Your account is pending approval. Please wait for admin approval before logging in.', 'info')
        
        return redirect(url_for('auth.login'))
    
    # Get roles for registration form (exclude admin)
    roles = Role.query.filter(Role.name != 'admin').all()
    return render_template('auth/register.html', roles=roles)

@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role.name == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role.name == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif current_user.role.name == 'nurse':
            return redirect(url_for('nurse.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if account is approved
            if not user.is_approved:
                flash('Your account is pending approval. Please wait for admin approval before logging in.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            
            # Role-based redirection
            if user.role.name == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role.name == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            elif user.role.name == 'nurse':
                return redirect(url_for('nurse.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Add this line to clear all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))