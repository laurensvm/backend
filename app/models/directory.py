# from app.exceptions import ValidationError
from datetime import datetime

from .. import db


class Directory(db.Model):
    __tablename__ = "directory"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=True)
    children = db.relationship("Directory", backref=db.backref('parent', remote_side=[id]))
    name = db.Column(db.String(256), index=True)
    path = db.Column(db.String(256), unique=True, index=True)
    size = db.Column(db.Integer, default=0, nullable=True)
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    users_with_rights = db.relationship("User", secondary="link")

    def to_json(self):
        json_post = {
            "id": self.id,
            "name": self.name,
            "format": self.format,
            "size": self.size,
            "path": self.path,
            "creation_date": self.creation_date,
            "parent_id": self.parent_id,
            "children": [ child.id for child in self.children ]
        }
        return json_post

    def has_child_with(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

    @staticmethod
    def exists(path, name):
        if Directory.query.filter_by(path=path).filter_by(name=name).first():
            return True
        return False

    @staticmethod
    def exists(path):
        if Directory.query.filter_by(path=path).first():
            return True
        return False