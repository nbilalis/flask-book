from random import choice
from functools import wraps

from flask import current_app as app

from flask import render_template, redirect, url_for, flash, session, request, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import and_, or_, func

from . import db
from .models import User, Post
from .forms import RegisterForm, LoginForm


def login_required(view):
    '''
    Decorate that checks if user os logged in
    by looking for username is session
    '''
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get('username') is None:
            flash('You need to login first!', category='warning')
            return redirect(url_for('login_register'))

        return view(**kwargs)

    return wrapped_view


@app.get('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/login-register', methods=['GET', 'POST'])
def login_register():
    '''
    Handle Login and Register
    Resources:
    Quickstart — Flask-WTF Documentation (0.15.x) - https://tmpl.at/3z4QwbG
    Form Validation with WTForms — Flask Documentation (2.0.x) - https://tmpl.at/3z9jrLS
    Handling forms — Explore Flask 1.0 documentation - https://tmpl.at/3esWA5M
    Multiple forms in a single page using flask and WTForms - Stack Overflow - https://tmpl.at/3yZctJg
    '''
    login_form = LoginForm()
    register_form = RegisterForm()

    if not login_form.username.data and (username := request.cookies.get('username')):
        login_form.username.data = username

    # Don't use `validate_on_submit()`
    # It will cause both forms to be populated

    if login_form.submit_login.data and login_form.validate():
        user = User.query.filter_by(
            username=login_form.username.data,
        ).one_or_none()

        if user is None or not check_password_hash(user.password, login_form.password.data):
            flash('Wrong username and / or password. Please try again!', category='danger')
        else:
            session['username'] = user.username
            res = make_response(redirect(url_for("profile", username=user.username)))
            res.set_cookie('username', user.username)
            return res

    if register_form.submit_register.data and register_form.validate():
        user = User.query.filter(
            (User.username == register_form.username.data) | (User.email == register_form.email.data)
        ).one_or_none()

        if user is not None:
            if user.username == register_form.username.data:
                flash('Username already taken!', category='warning')
            else:
                flash('Someone has already registered with this E-mail address!', category='warning')
        else:
            user = User(
                username=register_form.username.data,
                password=generate_password_hash(register_form.password.data),
                email=register_form.email.data,
                firstname=register_form.firstname.data,
                lastname=register_form.lastname.data,
            )
            db.session.add(user)
            db.session.commit()

            flash('Registration successful!', category='success')

            session['username'] = user.username
            return redirect(url_for("profile", username=register_form.username.data))

    # First visit of vaidation errors
    return render_template('login_register.html', register_form=register_form, login_form=login_form)


@app.get('/logout')
def logout():
    '''
    Logout the use by clearing teh session
    '''
    session.clear()     # session.pop('username')
    return redirect(url_for('login_register'))


@app.get('/profile/')
@app.get('/profile/<username>')
@login_required
def profile(username=None):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('profile.html', user=user)


@app.get('/test')
def test():
    users_alphabetically = User.query.order_by(User.lastname, User.firstname).all()
    random_user = choice(users_alphabetically)

    post_count_sub = Post.query.filter(Post.author_id == User.id).with_entities(func.count(Post.id).label('post_count')).scalar_subquery()
    last_post_per_user_sub = Post.query.with_entities(Post.author_id, func.max(Post.created_at).label('last_post_ts')).group_by(Post.author_id).subquery()

    context = {
        'first_user': User.query.first(),
        'users_alphabetically': users_alphabetically,
        'user_posts': Post.query.with_parent(random_user).all(),
        'user_post_count': Post.query.with_parent(random_user).with_entities(func.count(Post.id).label('post_count')).scalar(),
        'usernames': User.query.options(load_only(User.username)).order_by(User.username).all(),
        'login_user': User.query.filter(and_(User.username == random_user.username, User.password == random_user.password)).one_or_none(),
        'ten_latest_posts': Post.query.options(joinedload(Post.author)).with_entities(Post, User).order_by(Post.created_at.desc()).limit(10).all(),
        'first_post_from_search': Post.query.filter(or_(Post.title.like('%est%'), Post.body.like('%est%'))).first(),
        # Here be dragons
        'user_with_post_count_1': User.query.join(Post).group_by(User).with_entities(User, func.count(Post.id).label('post_count')).all(),
        'user_with_post_count_2': User.query.with_entities(User, post_count_sub.label('post_count')).all(),
        'users_with_their_latest_post_1': User.query.join(Post).with_entities(User, Post).filter(and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)).all(),
        'users_with_their_latest_post_2': User.query.join(Post).join(last_post_per_user_sub, and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)).with_entities(User, Post).all(),
    }

    return render_template('test.html', context=context)
