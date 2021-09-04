from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload, subqueryload

from marshmallow import ValidationError

from . import db

from .models import User, Post
from .schemas import UserSchema, PostSchema

bp = Blueprint('api', __name__, url_prefix='/api/v1')


@bp.route('/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    schema = UserSchema(many=True, only=('id', 'username', 'email', 'firstname', 'lastname'))

    return jsonify(schema.dump(users))


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.options(subqueryload(User.posts)).get(id)
    schema = UserSchema(only=('id', 'username', 'email', 'firstname', 'lastname', 'posts'))

    if user is not None:
        return schema.dump(user)
    else:
        return {'message': 'Post not found'}, 404


@bp.route('/posts/', methods=['GET'])
def get_posts():
    posts = Post.query.options(subqueryload(Post.author)).all()
    schema = PostSchema(many=True)

    return jsonify(schema.dump(posts))


@bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.options(joinedload(Post.author)).get(id)
    schema = PostSchema()

    if post is not None:
        return schema.dump(post)
    else:
        return {'message': 'Post not found'}, 404


@bp.route('/posts/', methods=['POST'])
def add_post():
    json_data = request.get_json()

    if not json_data:
        return {'message': 'No input data provided'}, 400

    try:
        schema = PostSchema()
        dict = schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    author = User.query.get(dict['author_id'])

    if author is None:
        return 422

    post = Post(body=dict['body'], author=author)

    db.session.add(post)
    db.session.commit()

    result = schema.dump(Post.query.options(joinedload(Post.author)).filter(Post.id == post.id).one())

    return {'message': 'Post created', 'post': result}, 201
