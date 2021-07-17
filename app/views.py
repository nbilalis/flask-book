from flask import current_app as app

from flask import render_template, redirect, url_for, flash
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import and_, or_, func

from .models import User, Post
from .forms import RegisterForm, LoginForm

from random import choice


@app.get('/')
def home():
    return render_template('home.html')



@app.route('/login-register', methods=['GET', 'POST'])
def login_register():
    '''
    Handle Login and Registef
    Resources:
    Quickstart — Flask-WTF Documentation (0.15.x) - https://tmpl.at/3z4QwbG
    Form Validation with WTForms — Flask Documentation (2.0.x) - https://tmpl.at/3z9jrLS
    Handling forms — Explore Flask 1.0 documentation - https://tmpl.at/3esWA5M
    Multiple forms in a single page using flask and WTForms - Stack Overflow - https://tmpl.at/3yZctJg
    '''
    login_form = LoginForm()
    register_form = RegisterForm()

    # Don't use `validate_on_submit()`
    # It will cause both forms to be populated

    if login_form.submit_login.data and login_form.validate():
        flash('Login successful!', category='success')
        return redirect(url_for("profile", username=login_form.username.data))

    if register_form.submit_register.data and register_form.validate():
        flash('Registration successful!', category='success')
        return redirect(url_for("profile", username=register_form.username.data))

    return render_template('login_register.html', register_form=register_form, login_form=login_form)


@app.get('/profile/')
@app.get('/profile/<username>')
def profile(username=None):
    return render_template('profile.html')


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
