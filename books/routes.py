# books/routes.py
from flask import Blueprint, render_template

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def index():
    """Renders the main books landing/listing page."""
    # You might want to list books here or redirect to search
    return "Books main page - not yet implemented for a specific HTML file."

@books_bp.route('/search')
def search():
    """Renders the book search page."""
    return render_template('books/search.html') # Points to templates/books/search.html

@books_bp.route('/<int:book_id>')
def book_detail(book_id):
    """Renders a single book's detail page."""
    # In a real app, you'd fetch book data based on book_id
    return render_template('books/detail.html', book_id=book_id) # Points to templates/books/detail.html