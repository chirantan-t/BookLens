# review/routes.py
from flask import Blueprint, render_template

review_bp = Blueprint('review', __name__)

@review_bp.route('/add')
def add_review():
    """Renders the page to add a new review."""
    return render_template('review/add.html') # Points to templates/review/add.html

@review_bp.route('/edit/<int:review_id>')
def edit_review(review_id):
    """Renders the page to edit an existing review."""
    # In a real app, you'd fetch review data based on review_id
    return render_template('review/edit.html', review_id=review_id) # Points to templates/review/edit.html