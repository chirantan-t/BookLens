# user/routes.py
from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    """Renders the user profile page."""
    return render_template('user/profile.html') # Points to templates/user/profile.html