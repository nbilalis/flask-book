from flask import current_app as app

from .models import User, Post

from flask import render_template


@app.get('/')
def home():
    return 'Welcome to Flask-book!'


@app.get('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)
