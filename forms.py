from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User # Import User model to check for uniqueness
from datetime import datetime # ADDED: Import datetime

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"class": "form-control"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"class": "form-control"})
    submit = SubmitField('Sign Up', render_kw={"class": "btn btn-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class BookForm(FlaskForm):
    """Form for adding/editing a book."""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)], render_kw={"class": "form-control"})
    author_name = StringField('Author', validators=[DataRequired(), Length(max=100)], render_kw={"class": "form-control"})
    isbn = StringField('ISBN (optional)', validators=[Length(max=13)], render_kw={"placeholder": "e.g., 978-0321765723", "class": "form-control"})
    publication_year = IntegerField('Publication Year (optional)', validators=[NumberRange(min=1000, max=datetime.now().year)], render_kw={"placeholder": f"e.g., {datetime.now().year}", "class": "form-control"})
    genre = StringField('Genre (optional)', validators=[Length(max=50)], render_kw={"class": "form-control"})
    description = TextAreaField('Description (optional)', render_kw={"rows": 5, "class": "form-control"})
    cover_image_url = StringField('Cover Image URL (optional)', render_kw={"placeholder": "e.g., http://example.com/cover.jpg", "class": "form-control"})
    submit = SubmitField('Save Book', render_kw={"class": "btn btn-primary"})

class ReviewForm(FlaskForm):
    """Form for adding/editing a review."""
    rating = IntegerField('Rating (1-5 Stars)', validators=[DataRequired(), NumberRange(min=1, max=5)], render_kw={"class": "form-control", "min": 1, "max": 5})
    comment = TextAreaField('Comment (optional)', validators=[Length(max=1000)], render_kw={"rows": 5, "class": "form-control"})
    submit = SubmitField('Post Review', render_kw={"class": "btn btn-primary"})