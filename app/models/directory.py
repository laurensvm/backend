from .. import db
from .base import Base

class Directory(Base):
    parent_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=True)
    children = db.relationship("Directory", backref=db.backref('parent', remote_side='Directory.id'))
    name = db.Column(db.String(256), index=True)
    path = db.Column(db.String(256), unique=True, index=True)
    size = db.Column(db.Integer, default=0, nullable=True)
    users_with_rights = db.relationship("User", secondary="link")

    def to_json(self):
        json_post = {
            "id": self.id,
            "name": self.name,
            "format": self.format,
            "size": self.size,
            "path": self.path,
            "timestamp": self.timestamp,
            "parent_id": self.parent_id,
            "children": [ child.id for child in self.children ]
        }
        return json_post

    def has_child_with(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

    def remove(self):
        for user in self.users_with_rights:
            user.directory_rights.remove(self)

        # Recursively removes all children
        # and also removes the user rights
        for child in self.children:
            child.remove()

        db.session.delete(self)
        db.session.commit()

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