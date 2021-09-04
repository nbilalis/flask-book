from . import ma
from .models import User, Post

# Flask-Marshmallow: Flask + marshmallow for beautiful APIs — Flask-Marshmallow 0.14.0 documentation - https://tmpl.at/3BDic8X


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    posts = ma.List(ma.HyperlinkRelated('main.api.get_post'))


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        # include_fk = True

    author = ma.HyperlinkRelated('main.api.get_user')
