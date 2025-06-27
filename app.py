# app.py
import os
from datetime import datetime
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Blueprint # Correctly imported Blueprint at the top
)
from extensions import db, login_manager, csrf, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

from models import User, Book, Review
from forms import RegistrationForm, LoginForm, BookForm, ReviewForm

app = Flask(__name__)
app.config.from_object('config.Config') # Load configuration from config.py

# Init extensions - Ensure correct order and instantiation
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app) # Initialize CSRFProtect with the app instance
bcrypt.init_app(app)

# Flask-Login configuration
login_manager.login_view = 'auth.login' # Points to the auth blueprint's login function
login_manager.login_message_category = 'info'

# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login requires a user_loader callback that returns a user object
    given a user ID.
    """
    return User.query.get(int(user_id))


# --- Define Blueprints and their routes ---

# Auth Blueprint
# template_folder points to the 'auth' directory itself, relative to app.py
auth_bp = Blueprint('auth', __name__, template_folder='auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data) # Use the set_password method from models.py
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email (as per your LoginForm)
        user = User.query.filter_by(email=form.email.data).first()
        # Check if user exists and password is correct using check_password method
        if user and user.check_password(form.password.data):
            # remember is a StringField in forms.py, so check its value (e.g., 'on' for checked)
            remember_me = (request.form.get('remember') == 'on') # Check if checkbox was checked
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- Books Blueprint ---
books_bp = Blueprint('books', __name__, template_folder='books')

@books_bp.route('/')
def books_index():
    books = Book.query.all()
    return render_template('search.html', books=books)

@books_bp.route('/search', methods=['GET', 'POST'])
def search():
    books = []
    if request.method == 'POST':
        search_query = request.form.get('query')
        if search_query:
            books = Book.query.filter(
                (Book.title.ilike(f'%{search_query}%')) |
                (Book.author_name.ilike(f'%{search_query}%'))
            ).all()
        else:
            books = Book.query.all()
    else:
        books = Book.query.all()
    return render_template('search.html', books=books)

@books_bp.route('/<int:book_id>')
def book_detail(book_id):
    book = db.session.get(Book, book_id) # Using db.session.get for primary key lookup
    if book is None: # Explicitly handle 404
        flash('Book not found!', 'danger')
        return redirect(url_for('books.books_index'))

    reviews = Review.query.filter_by(book_id=book_id).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, reviewer_id=current_user.id).first()
    return render_template('detail.html', book=book, reviews=reviews, user_review=user_review)

@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author_name=form.author_name.data,
            isbn=form.isbn.data,
            publication_year=form.publication_year.data,
            genre=form.genre.data,
            description=form.description.data,
            cover_image_url=form.cover_image_url.data,
            # Assign current user as author (if they are adding it)
            author_id=current_user.id
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=new_book.id))
    return render_template('add_book.html', form=form, title='Add New Book')

@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None: # Explicitly handle 404
        flash('Book not found!', 'danger')
        return redirect(url_for('books.books_index'))

    # Only allow the original author to edit for now
    if book.author_id != current_user.id:
        flash('You are not authorized to edit this book.', 'danger')
        return redirect(url_for('books.book_detail', book_id=book.id))

    form = BookForm(obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=book.id))
    return render_template('edit_book.html', form=form, title='Edit Book', book=book)


# Review Blueprint
review_bp = Blueprint('review', __name__, template_folder='review')

@review_bp.route('/add/<int:book_id>', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = db.session.get(Book, book_id)
    if book is None: # Explicitly handle 404
        flash('Book not found!', 'danger')
        return redirect(url_for('books.books_index'))

    existing_review = Review.query.filter_by(book_id=book_id, reviewer_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this book. You can edit your existing review.', 'info')
        return redirect(url_for('review.edit_review', review_id=existing_review.id))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            book_id=book.id,
            reviewer_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Review posted successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=book.id))
    return render_template('add.html', form=form, book=book)

@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None: # Explicitly handle 404
        flash('Review not found!', 'danger')
        return redirect(url_for('books.books_index')) # Redirect to book index if review not found

    if review.reviewer_id != current_user.id:
        flash('You are not authorized to edit this review.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book.id)) # Redirect to book detail if not authorized

    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.comment = form.comment.data
        db.session.commit()
        flash('Review updated successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=review.book.id))
    return render_template('edit.html', form=form, review=review)

@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None: # Explicitly handle 404
        flash('Review not found!', 'danger')
        return redirect(url_for('books.books_index'))

    if review.reviewer_id != current_user.id:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book.id))

    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('books.book_detail', book_id=book_id))


# User Blueprint
user_bp = Blueprint('user', __name__, template_folder='user')

@user_bp.route('/profile')
@login_required
def profile():
    user_reviews = Review.query.filter_by(reviewer_id=current_user.id).all()
    user_books_authored = Book.query.filter_by(author_id=current_user.id).all()
    return render_template('profile.html', user=current_user, user_reviews=user_reviews, user_books_authored=user_books_authored)


# Register blueprints with the app
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(review_bp, url_prefix='/review')
app.register_blueprint(user_bp, url_prefix='/user')

# Main app route (index)
@app.route('/')
def index():
    """Renders the main landing page (index.html)."""
    return render_template('index.html')

if __name__ == '__main__':
    # Create the instance folder if it doesn't exist (for app.db)
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    with app.app_context():
        db.create_all() # Creates database tables based on models
    app.run(debug=True, port=5005) # Run the app on port 5000 in debug mode