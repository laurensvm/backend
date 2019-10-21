from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, g

from .. import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    directory_rights = db.relationship("Directory", secondary="link")

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    def set_is_admin(self, value):
        if g.current_user.is_admin:
            self.admin = value
        else:
            print("{0} has insufficient rights".format(g.current_user))


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
        except Exception:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def exists(username, email):
        if not User.query.filter_by(username=username).first():
            if not User.query.filter_by(email=email).first():
                return False
            return True
        return True

    def __repr__(self):
        return 'User {0}'.format(self.username)

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
        }