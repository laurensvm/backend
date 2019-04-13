from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, g
from app.exceptions import ValidationError
from datetime import datetime

from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    print(User.query.get(int(user_id)))
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config["SECRET_KEY"],
            expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return 'User {0}'.format(self.username)

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
        }


class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), unique=True, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)

    def to_json(self):
        json_post = {
            "id": self.id,
            "url": self.url,
            "timestamp": self.timestamp,
            "user_id": self.user_id
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        print(json_post)
        url = json_post.get("url")
        if url is None or url == '':
            raise ValidationError('Track does not have a url')
        return Track(url=url, user_id=g.current_user.id)
