from datetime import datetime
from extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship # Import relationship
from werkzeug.security import generate_password_hash, check_password_hash # ADD THIS LINE

class User(db.Model, UserMixin):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Store hashed passwords
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Keep this from previous versions

    # Relationships
    books_authored = relationship('Book', back_populates='author', lazy=True, foreign_keys='Book.author_id')
    reviews = relationship('Review', back_populates='reviewer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Flask-Login required method
    def get_id(self):
        return str(self.id)

    # ADD THESE TWO METHODS FOR PASSWORD HANDLING
    def set_password(self, password):
        """Hashes the password and sets it to password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    """Book model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Optional: if users can add books
    author_name = db.Column(db.String(100), nullable=False) # For external authors
    isbn = db.Column(db.String(13), unique=True, nullable=True) # ISBN-13
    publication_year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    author = relationship('User', back_populates='books_authored', foreign_keys=[author_id])
    reviews = relationship('Review', back_populates='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title} by {self.author_name}>'

class Review(db.Model):
    """Review model."""
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    book = relationship('Book', back_populates='reviews')
    reviewer = relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review for {self.book_id} by {self.reviewer_id} - {self.rating} stars>'