
# from flask import current_app as app

from . import app                   # from app import app
from .models import User             # from app.models import User

from flask import render_template


@app.get('/')
def home():
    return 'Welcome to Flask-book!'


@app.get('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)
