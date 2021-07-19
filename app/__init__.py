from os import environ, path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from flask_debugtoolbar import DebugToolbarExtension

BASE_PATH = path.dirname(path.abspath(__file__))

db = SQLAlchemy()                   # API — Flask-SQLAlchemy Documentation (2.x) - https://tmpl.at/3htQ8w9
migrate = Migrate()                 # Flask-Migrate — Flask-Migrate documentation - https://tmpl.at/3yg9ZWz
login_manager = LoginManager()      # Flask-Login — Flask-Login 0.4.1 documentation - https://bit.ly/2Uo7fba
boostrap = Bootstrap()              # Flask-Bootstrap — Flask-Bootstrap 3.3.7.1 documentation - https://tmpl.at/3k82RHR
toolbar = DebugToolbarExtension()   # Flask-DebugToolbar — Flask-DebugToolbar 0.12.dev0 documentation - https://tmpl.at/3Arw2LC


def create_app(test_config=None):
    '''
    Application Factory
    Application Factories — Flask Documentation (2.0.x) - https://tmpl.at/3hMud3J
    '''

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # python -c "import os; print(os.urandom(24).hex())"
        # python -c "import secrets; print(secrets.token_urlsafe(24))"
        SECRET_KEY=environ.get('SECRET_KEY', '1234'),
        SQLALCHEMY_DATABASE_URI='sqlite:///data/flask-book.db',                                 # 3 slashes = relative path
        # SQLALCHEMY_DATABASE_URI=f"sqlite:////{path.join(BASE_PATH, 'data/flask-book.db')}",   # 4 slashes = absolute path
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True,
        DEBUG_TB_INTERCEPT_REDIRECTS=False,
        # USE_SESSION_FOR_NEXT=True
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login — Flask-Login 0.4.1 documentation - https://bit.ly/3zfPt98
    login_manager.login_view = 'login_register'
    login_manager.login_message = 'You need to login first!'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)

    boostrap.init_app(app)
    toolbar.init_app(app)

    with app.app_context():
        from . import models    # noqa: E402, F401
        from . import views     # noqa: E402, F401
        from . import commands  # noqa: E402, F401

        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

    return app
