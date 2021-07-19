from random import choice

from flask import current_app as app
from flask import render_template, redirect, url_for, flash, session, request, abort

from werkzeug.security import check_password_hash, generate_password_hash
from is_safe_url import is_safe_url

from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import and_, or_, func

from flask_login import login_user, logout_user, login_required

from . import db

from .models import User, Post
from .forms import RegisterForm, LoginForm


@app.get('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/login-register', methods=['GET', 'POST'])
def login_register():
    '''
    Handle Login and Register

    Resources:
    Blueprints and Views — Flask Documentation (2.0.x) - https://bit.ly/3xPaEys
    Multiple forms in a single page using flask and WTForms - Stack Overflow - https://bit.ly/3kxEHXu
    How To Add Authentication to Your App with Flask-Login | DigitalOcean - https://do.co/3wK4Vsk
    Flask-Login — Flask-Login 0.4.1 documentation - https://bit.ly/3zfPt98
    Flask-Security — Flask-Security 3.0.0 documentation - https://bit.ly/36HOdiK
    '''

    # Initialize the two forms.
    # We manually pass `request.form` or `None`,
    # because the two forms use fields with same names (should we change that?)
    # If they are not initialized this way, values posted from one form,
    # appears to the other one too.
    login_form = LoginForm(request.form if request.form.get('submit_login') else None)
    register_form = RegisterForm(request.form if request.form.get('submit_register') else None)

    """ if not login_form.username.data and (username := request.cookies.get('username')):
        login_form.username.data = username """

    # If `LoginForm` was submitted and validated
    if login_form.validate_on_submit():
        # Get the user from the DB by their `username`
        user = User.query.filter_by(
            username=login_form.username.data,
        ).one_or_none()

        # User not found or password hashes don't match
        if user is None or not check_password_hash(user.password, login_form.password.data):
            flash('Wrong username and / or password. Please try again!', category='danger')
        else:
            # Successfull login!
            login_user(user, remember=True)

            next = request.args.get('next') or session.get('next')

            if next is not None and not is_safe_url(next, {request.host}):
                return abort(400)

            return redirect(next or url_for('profile', username=user.username))

    # If `RegisterForm` was submitted and validated
    if register_form.validate_on_submit():
        # Check for existing user with same `username` or `email`
        user = User.query.filter(
            (User.username == register_form.username.data) | (User.email == register_form.email.data)
        ).one_or_none()

        # If `username` or `email` is already used
        if user is not None:
            if user.username == register_form.username.data:
                flash('Username already taken!', category='warning')
                register_form.username.data = None
                register_form.username.errors.append('Username already taken!')
            else:
                register_form.email.data = None
                register_form.email.errors.append('Someone has already registered with this e-mail address!')
        else:
            # Successfull registration!

            # Set a new `User` object
            # python - Flask - how do I combine Flask-WTF and Flask-SQLAlchemy to edit db models? - Stack Overflow - https://bit.ly/3iiCNHm
            user = User()
            register_form.populate_obj(user)
            user.password = generate_password_hash(register_form.password.data)

            # Persist it in the DB
            db.session.add(user)
            db.session.commit()

            flash('Registration successful!', category='success')

            # "Log" them me automatically
            login_user(user, remember=True)

            # Redirect them to their profile page
            return redirect(url_for("profile", username=user.username))

    # First visit of vaidation errors
    return render_template('login_register.html', register_form=register_form, login_form=login_form)


@app.get('/logout')
def logout():
    '''
    Logout the user
    '''
    logout_user()
    return redirect(url_for('login_register'))


@app.get('/profile/')
@app.get('/profile/<username>')
@login_required
def profile(username=None):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('profile.html', user=user)

#
# Here be dragons
# -------------------------------------------------- #

@app.get('/test')
def test():
    '''
    Hit the '/test' route to see some queries in action
    '''
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

        # Here be more dragons
        'user_with_post_count_1': User.query.join(Post).group_by(User).with_entities(User, func.count(Post.id).label('post_count')).all(),
        'user_with_post_count_2': User.query.with_entities(User, post_count_sub.label('post_count')).all(),
        'users_with_their_latest_post_1': User.query.join(Post).with_entities(User, Post).filter(and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)).all(),
        'users_with_their_latest_post_2': User.query.join(Post).join(last_post_per_user_sub, and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)).with_entities(User, Post).all(),
    }

    return render_template('test.html', context=context)
