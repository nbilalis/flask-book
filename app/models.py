# type: ignore

from . import db        # from app import db

from datetime import datetime
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.engine import Engine


# python - Sqlite / SQLAlchemy: how to enforce Foreign Keys? - Stack Overflow - https://tmpl.at/3AubFgO
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


# python - SQLAlchemy Many-to-Many Relationship on a Single Table - Stack Overflow - https://tmpl.at/3wdjlRp
friendships = db.Table(
    'friendships',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    db.Column('followee_id', db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), index=True, unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)

    # posts = db.relationship('Post', backref=db.backref('author', cascade="all, delete"), lazy=False, passive_deletes=True)

    followers = db.relationship(
        'User',
        secondary=friendships,
        primaryjoin=id == friendships.c.follower_id,
        secondaryjoin=id == friendships.c.followee_id,
        backref="followees",
        cascade="all, delete",
        lazy='subquery'
    )

    def __repr__(self):
        return f'<User {self.id=} {self.username=}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    # time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    author = db.relationship('User', backref='posts', lazy=False)     # , foreign_keys=[author_id]

    # comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f'<Post {self.title=} {self.author_id=}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    author = db.relationship('User', backref='comments')

    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref='comments', lazy=True)

    def __repr__(self):
        return f'<Post {self.title=} {self.author_id=}>'
