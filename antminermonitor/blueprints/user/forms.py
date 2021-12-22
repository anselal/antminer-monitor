from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.validators import EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=5, max=64)])
    password = PasswordField(
        'Password', validators=[
            Length(min=6, max=128),
        ])
    remember = BooleanField('Remember me')


class PasswordResetForm(FlaskForm):
    # username = TextField('Username', validators=[Length(min=5, max=64)])
    username = SelectField('Username')
    password = PasswordField(
        'New Password',
        validators=[
            Length(min=6, max=128),
            EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Repeat Password')
