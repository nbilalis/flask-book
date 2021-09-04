from . import ma
from .models import User, Post


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_fk = True
