from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# python -c "import os; print(os.urandom(24).hex())"
# python -c "import secrets; print(secrets.token_urlsafe(24))"
app.secret_key = environ.get('SECRET_KEY', '1234')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/flask-book.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)

from . import models        # noqa: F401, E402
from . import views         # noqa: F401, E402
from . import commands      # noqa: F401, E402
