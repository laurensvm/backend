from .. import db

from . import User, Directory

class Link(db.Model):
    __tablename__ = "link"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    directory_id = db.Column(db.Integer, db.ForeignKey("directory.id"), primary_key=True)
