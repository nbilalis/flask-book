from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, abort

from werkzeug.security import check_password_hash, generate_password_hash
from is_safe_url import is_safe_url

from sqlalchemy.orm import load_only, joinedload, selectinload   # , subqueryload
from sqlalchemy.sql import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from flask_login import login_user, logout_user, login_required, current_user

from . import db

from .models import User, Post
from .forms import RegisterForm, LoginForm, PostForm

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    post_form = PostForm()

    latest_posts = Post.query.options(selectinload(Post.author)).order_by(Post.created_at.desc()).slice(0, 30).all()

    if post_form.validate_on_submit():      # POST
        try:
            post = Post(body=post_form.body.data, author=current_user)
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError as e:
            flash('Something went wrong! Please try again later or contact the administrator in case the error persists.', category='danger')
            app.logger.error(e)

        return redirect(url_for('main.home'))
    else:                                   # GET
        return render_template('home.html', post_form=post_form, latest_posts=latest_posts)


@bp.route('/login-register', methods=['GET', 'POST'])
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

    # ``.is_submitted()` is trash.
    # It just checks if there was a `POST`
    login_form_submitted = request.form.get('submit_login')
    register_form_submitted = request.form.get('submit_register')

    # Initialize the two forms.
    # We manually pass `request.form` or `None`,
    # because the two forms use fields with same names (should we change that?)
    # If they are not initialized this way, values posted from one form,
    # appears to the other one too.
    login_form = LoginForm(request.form if login_form_submitted else None)
    register_form = RegisterForm(request.form if register_form_submitted else None)

    # If `LoginForm` was submitted and validated
    if login_form_submitted and login_form.validate():
        # Get the user from the DB by their `username`
        user = User.query.filter_by(username=login_form.username.data).one_or_none()

        # User not found or password hashes don't match
        if user is None or not check_password_hash(user.password, login_form.password.data):
            flash('Wrong username and / or password. Please try again!', category='danger')

            # Error: Form responses must redirect to another location · Issue #12 · hotwired/turbo-rails - https://bit.ly/2V05S2A
            return render_template('login_register.html', register_form=register_form, login_form=login_form), 422
        else:
            # Successfull login!
            login_user(user, remember=True)

            next = request.args.get('next') or session.get('next')

            if next is not None and not is_safe_url(next, {request.host}):
                return abort(400)
            else:
                return redirect(next or url_for('main.profile', username=user.username))

    # If `RegisterForm` was submitted and validated
    if register_form.is_submitted():
        # Check for existing user with same `username` or `email`
        u1 = User.query.filter_by(username=register_form.username.data).one_or_none()
        u2 = User.query.filter_by(email=register_form.email.data).one_or_none()

        if register_form.validate() and (u1 or u2) is not None:   # Beware, order or expessions
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
            return redirect(url_for('main.profile', username=user.username))

        # If `username` or `email` is already used
        if u1 is not None:
            register_form.username.errors.append('Username is taken!')

        if u2 is not None:
            register_form.email.errors.append('Someone has already registered with this e-mail address!')

        # Error: Form responses must redirect to another location · Issue #12 · hotwired/turbo-rails - https://bit.ly/2V05S2A
        return render_template('login_register.html', register_form=register_form, login_form=login_form), 422

    # First visit of vaidation errors
    return render_template('login_register.html', register_form=register_form, login_form=login_form)


@bp.get('/logout')
def logout():
    '''
    Logout the user
    '''
    logout_user()
    return redirect(url_for('main.login_register'))


@bp.get('/profile/')
@bp.get('/profile/<username>')
@login_required
def profile(username=None):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('profile.html', user=user)

#
# Here be dragons
# -------------------------------------------------- #


@bp.get('/test')
def test():
    '''
    Hit the '/test' route to see some queries in action
    '''
    from random import choice

    users_alphabetically = User.query.order_by(User.lastname, User.firstname).all()
    random_user = choice(users_alphabetically)

    post_count_sub = Post.query.filter(Post.author_id == User.id).with_entities(func.count(Post.id).label('post_count')).scalar_subquery()
    last_post_per_user_sub = Post.query.with_entities(
        Post.author_id, func.max(Post.created_at).label('last_post_ts')
    ).group_by(Post.author_id).subquery()

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
        'users_with_their_latest_post_1': User.query.join(Post).with_entities(User, Post).filter(
            and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)
        ).all(),
        'users_with_their_latest_post_2': User.query.join(Post).join(
            last_post_per_user_sub,
            and_(User.id == last_post_per_user_sub.c.author_id, Post.created_at == last_post_per_user_sub.c.last_post_ts)
        ).with_entities(User, Post).all(),
    }

    return render_template('test.html', context=context)
