from flask import current_app as app

from . import db                # from app import db
from .models import User, Post  # from app.models import User, Post


from random import randint, choice, sample
from datetime import datetime, timedelta
from lorem import sentence, paragraph


@app.cli.command('init-db')
def init_db():
    db.drop_all()
    db.create_all()


@app.cli.command('add-data')
def add_data():
    User.query.delete()

    db.session.commit()

    users = []

    users.append(User(username='haris', lastname='Argyropoulos', firstname='Zacharias-Christos', password='1234'))
    users.append(User(username='ioanna', lastname='Mitsani', firstname='Ioanna', password='1234'))
    users.append(User(username='stavros', lastname='Tsiogkas', firstname='Stavros', password='1234'))
    users.append(User(username='marios', lastname='Tsioutsis', firstname='Marios', password='1234'))

    users.append(User(username='george', lastname='Sisko', firstname='George', password='1234'))
    users.append(User(username='lena', lastname='Lekkou', firstname='Lena', password='1234'))
    users.append(User(username='nikos.a', lastname='Apostolakis', firstname='Nikolaos', password='1234'))
    users.append(User(username='nikos.b', lastname='Bilalis', firstname='Nikolaos', password='1234'))

    for u in users:
        u.followers = [f for f in sample(users, randint(1, len(users))) if f != u]
        db.session.add(u)

    ts = datetime.now() - timedelta(weeks=6*4)    # .utcnow()

    while datetime.now() >= ts:
        p = Post(title=sentence(), body=paragraph(), created_at=ts)
        u = choice(users)
        u.posts.append(p)
        ts += timedelta(microseconds=randint(1, 10**11))

    db.session.commit()
