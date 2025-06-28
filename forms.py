from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField
# Import new validators: Regexp, Optional, URL
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Regexp, Optional, URL
from models import User # Import User model to check for uniqueness
from datetime import datetime

class RegistrationForm(FlaskForm):
    """Form for user registration with strong password requirements."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'.*[A-Z].*', message='Password must contain at least one uppercase letter.'),
        Regexp(r'.*[a-z].*', message='Password must contain at least one lowercase letter.'),
        Regexp(r'.*\d.*', message='Password must contain at least one number.'),
        Regexp(r'.*[@$!%*?&_#].*', message='Password must contain at least one special character (e.g., @$!%*?&_#).') # Added underscore and hash for example
    ], render_kw={"class": "form-control"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')], render_kw={"class": "form-control"})
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
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login', render_kw={"class": "btn btn-primary"})

class BookForm(FlaskForm):
    """Form for adding/editing a book."""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)], render_kw={"class": "form-control"})
    author_name = StringField('Author', validators=[DataRequired(), Length(max=100)], render_kw={"class": "form-control"})
    isbn = StringField('ISBN (optional)', validators=[Length(max=13)], render_kw={"placeholder": "e.g., 978-0321765723", "class": "form-control"})
    publication_year = IntegerField('Publication Year (optional)', validators=[NumberRange(min=1000, max=datetime.now().year)], render_kw={"placeholder": f"e.g., {datetime.now().year}", "class": "form-control"})
    genre = StringField('Genre (optional)', validators=[Length(max=50)], render_kw={"class": "form-control"})
    description = TextAreaField('Description (optional)', render_kw={"rows": 5, "class": "form-control"})
    # Using Optional and URL validators for image URL
    cover_image_url = StringField('Cover Image URL (optional)', validators=[Optional(), URL(message='Must be a valid URL')], render_kw={"placeholder": "e.g., http://example.com/cover.jpg", "class": "form-control"})
    submit = SubmitField('Save Book', render_kw={"class": "btn btn-primary"})

class ReviewForm(FlaskForm):
    """Form for adding/editing a review."""
    rating = IntegerField('Rating (1-5 Stars)', validators=[DataRequired(), NumberRange(min=1, max=5)], render_kw={"class": "form-control", "min": 1, "max": 5})
    comment = TextAreaField('Comment (optional)', validators=[Length(max=1000)], render_kw={"rows": 5, "class": "form-control"})
    submit = SubmitField('Post Review', render_kw={"class": "btn btn-primary"})

class EditProfileForm(FlaskForm):
    """Form for editing user profile."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    submit = SubmitField('Update Profile', render_kw={"class": "btn btn-primary"})

    # Custom validation to ensure uniqueness when editing (excluding current user's original data)
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username: # Only check if username has changed
            user = User.query.filter_by(username=self.username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email: # Only check if email has changed
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class CsrfOnlyForm(FlaskForm):
    """A simple form to provide a CSRF token for forms that don't need other fields."""
    # No fields needed, Flask-WTF will still generate the CSRF token
    pass