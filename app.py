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
    Blueprint
)
from extensions import db, login_manager, csrf, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

# IMPORTANT: Ensure models.py and forms.py are at the same level as app.py
from models import User, Book, Review
# Import all forms, including the new EditProfileForm and CsrfOnlyForm
from forms import RegistrationForm, LoginForm, BookForm, ReviewForm, CsrfOnlyForm, EditProfileForm

app = Flask(__name__)
app.config.from_object('config.Config') # Load configuration from config.py

# Init extensions
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
    return db.session.get(User, int(user_id)) # Using db.session.get for consistency


# --- Define Blueprints and their routes ---

# Auth Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
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
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            remember_me = form.remember.data
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
    logout_user() # This clears the user's session
    flash('You have been logged out.', 'info') # This displays a message on the next page loaded
    # Standard practice to redirect after logout, typically to login or index
    return redirect(url_for('auth.login'))


# --- Books Blueprint ---
books_bp = Blueprint('books', __name__, template_folder='templates/books')

@books_bp.route('/') # This route will be /books/
def books_index():
    books = Book.query.all()
    # This route could be a landing page for books, or just redirect to search
    # Passing a form here for consistency with the search route template
    form = CsrfOnlyForm()
    return render_template('search.html', books=books, form=form)

@books_bp.route('/search', methods=['GET', 'POST']) # This route will be /books/search
def search():
    books = []
    # Instantiate a form for CSRF protection for the search bar (it's a POST form)
    form = CsrfOnlyForm()

    if request.method == 'POST':
        # CSRF token validation is handled by Flask-WTF for forms,
        # but if you're using request.form.get directly without form.validate_on_submit(),
        # ensure csrf.protect() is active for the route or manually checked.
        # Given how csrf is initialized, it should auto-protect POSTs.
        search_query = request.form.get('query')
        if search_query:
            books = Book.query.filter(
                (Book.title.ilike(f'%{search_query}%')) |
                (Book.author_name.ilike(f'%{search_query}%')) | # Added back author_name search
                (Book.genre.ilike(f'%{search_query}%')) # Added genre search
            ).all()
        else:
            books = Book.query.all()
    else: # GET request
        books = Book.query.all() # Display all books on initial GET request
    return render_template('search.html', books=books, form=form) # Pass the form to the template

@books_bp.route('/<int:book_id>') # This route will be /books/<int:book_id>
def book_detail(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.books_index'))

    reviews = Review.query.filter_by(book_id=book_id).all()
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, reviewer_id=current_user.id).first()

    # Instantiate a form for CSRF protection for the delete review button in detail.html
    delete_form = CsrfOnlyForm()
    return render_template('detail.html', book=book, reviews=reviews, user_review=user_review, form=delete_form)

@books_bp.route('/add', methods=['GET', 'POST']) # This route will be /books/add
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
            author_id=current_user.id # Assign current user as author
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=new_book.id))
    return render_template('add_book.html', form=form, title='Add New Book')

@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST']) # This route will be /books/edit/<int:book_id>
@login_required
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.books_index'))

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
review_bp = Blueprint('review', __name__, template_folder='templates/review')

@review_bp.route('/add/<int:book_id>', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
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
            comment=form.comment.data,
            date_posted=datetime.utcnow() # Correct attribute name
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
    if review is None:
        flash('Review not found!', 'danger')
        return redirect(url_for('books.books_index'))

    if review.reviewer_id != current_user.id:
        flash('You are not authorized to edit this review.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book_id))

    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.comment = form.comment.data
        # date_posted is a creation timestamp, usually not updated on edit
        db.session.commit()
        flash('Review updated successfully!', 'success')
        return redirect(url_for('books.book_detail', book_id=review.book_id))
    return render_template('edit.html', form=form, review=review)

@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None:
        flash('Review not found!', 'danger')
        return redirect(url_for('books.books_index'))

    if review.reviewer_id != current_user.id:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book_id))

    book_id = review.book_id # Get book_id before deleting the review
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('books.book_detail', book_id=book_id))


# User Blueprint
user_bp = Blueprint('user', __name__, template_folder='templates/user')

@user_bp.route('/profile')
@login_required
def profile():
    user_reviews = Review.query.filter_by(reviewer_id=current_user.id).all()
    user_books_authored = Book.query.filter_by(author_id=current_user.id).all()
    # Instantiate a form for CSRF protection for any potential forms in profile.html (e.g., delete review)
    profile_form = CsrfOnlyForm()
    return render_template('profile.html', user=current_user, user_reviews=user_reviews, user_books_authored=user_books_authored, form=profile_form)

@user_bp.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Instantiate the form, passing current user's username and email for unique validation
    form = EditProfileForm(original_username=current_user.username, original_email=current_user.email)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        # Populate form fields with current user data on GET request (initial load)
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('edit_profile.html', title='Edit Profile', form=form) # Renders templates/user/edit_profile.html


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
    app.run(debug=True, port=5007) # Run the app on port 5007 in debug mode (consistent with your last provided port)