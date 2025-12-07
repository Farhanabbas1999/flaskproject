import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, Role

@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user via command line."""
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        click.echo('Error: Username already exists!')
        return
    
    if User.query.filter_by(email=email).first():
        click.echo('Error: Email already exists!')
        return
    
    # Get or create admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
        db.session.commit()
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role_id=admin_role.id,
        is_active=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'✓ Admin user "{username}" created successfully!')