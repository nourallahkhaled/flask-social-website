# Imports
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskproj.models import User


# Classes that repreasent our forms in python
class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=2, max=20)
        ],
        render_kw={'placeholder': 'Enter your Username'}
    )
    gender = SelectField(
        'Gender',
        choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female')],
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ],
        render_kw={'placeholder': 'Enter your Email'}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ],
        render_kw={'placeholder': 'Enter your Password'}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
        ],
        render_kw={'placeholder': 'Confirm your Password'}
    )
    submit = SubmitField(
        'Sign Up'
    )

    # Custom Validation Functions for duplicats
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Email is taken, please choose another Email")

class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ],
        render_kw={'placeholder': 'Enter your Email'}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ],
        render_kw={'placeholder': 'Enter your Password'}
    )
    submit = SubmitField(
        'Login'
    )



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=1000)])
    privacy = SelectField('Privacy', choices=[('public', 'Public'), ('private', 'Private'),('friends', 'Friends')])
    submit = SubmitField(
        'Create'
    )
    
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update')