from flask_wtf import FlaskForm     # Flask-WTF — Flask-WTF Documentation (0.15.x) - https://tmpl.at/36puWCq
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Username', description='Username', validators=[DataRequired()])
    password = PasswordField('Password', description='Password', validators=[DataRequired()])
    submit_login = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', description='Username', validators=[DataRequired(), Length(min=4, max=16)])
    password = PasswordField('Password', description='Password', validators=[DataRequired(), Length(min=8, max=32)])
    email = EmailField('E-Mail', description='E-Mail', validators=[DataRequired(), Email()])
    firstname = StringField('Firstname', description='Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', description='Lastname', validators=[DataRequired()])
    submit_register = SubmitField('Register')


class PostForm(FlaskForm):
    body = StringField('Body', description='Make a post…', validators=[DataRequired(), Length(min=3, max=160)])
    submit_post = SubmitField('Post')
