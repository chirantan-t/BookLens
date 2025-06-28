# auth/routes.py
from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register')
def register():
    """Renders the registration page."""
    return render_template('auth/register.html') # Points to templates/auth/register.html

@auth_bp.route('/login')
def login():
    """Renders the login page."""
    return render_template('auth/login.html') # Points to templates/auth/login.html

@auth_bp.route('/profile')
def profile():
    """Renders the user profile page."""
    return render_template('user/profile.html') 

# Add other auth-related routes here (e.g., /logout, /forgot_password)