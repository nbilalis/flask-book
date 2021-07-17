from flask_wtf import FlaskForm     # Flask-WTF — Flask-WTF Documentation (0.15.x) - https://tmpl.at/36puWCq
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Username', description='Username', validators=[DataRequired(), Length(min=8, max=32)])
    password = PasswordField('Password', description='Password', validators=[DataRequired(), Length(min=8, max=32)])
    submit_login = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', description='Username', validators=[DataRequired(), Length(min=8, max=32)])
    password = PasswordField('Password', description='Password', validators=[DataRequired(), Length(min=8, max=32)])
    email = StringField('E-Mail', description='E-Mail', validators=[DataRequired(), Email()])
    submit_register = SubmitField('Register')
