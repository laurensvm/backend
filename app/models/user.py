from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from flask_login import UserMixin
from flask import current_app, g

from .. import db, login_manager
from .base import Base


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, Base):
    __tablename__ = "user"
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    files = db.relationship("File", back_populates="user")
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
    def unique(username, email):
        return User.query.filter(
            or_(User.email == email,
                 User.username == username)
        ).first() is None

    @staticmethod
    def exists(user_email_id):
        return User.query.filter(
            or_(User.username == user_email_id,
                User.email == user_email_id,
                User.id == user_email_id)
        ).first() is not None

    @staticmethod
    def create_superuser():
        username = current_app.config["ADMIN_USERNAME"]
        password = current_app.config["ADMIN_PASSWORD"]
        email = current_app.config["ADMIN_EMAIL"]

        u = User(username=username, email=email, password=password)
        u.admin = True

        u.save()

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def remove(self):
        self.directory_rights = []
        super(User, self).remove()

    def __repr__(self):
        return 'User <{0}>'.format(self.username)

    def json(self):
        json = super(User, self).json()
        json.update({
            "email": self.email,
            "username": self.username,
            "admin": self.admin,
            "files": [ file.name for file in self.files ],
            "directory_rights": [ directory.name for directory in self.directory_rights ]
        })
        return json

