from .. import db
from .base import Base

class Directory(Base):
    __tablename__ = "directory"
    parent_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=True)
    children = db.relationship("Directory", backref=db.backref('parent', remote_side='Directory.id'))
    files = db.relationship("File", back_populates="directory")
    name = db.Column(db.String(256), index=True)
    path = db.Column(db.String(256), unique=True, index=True)
    size = db.Column(db.Integer, default=0)
    users_with_rights = db.relationship("User", secondary="link")

    def json(self):
        json = super(Directory, self).json()
        return json.update({
            "parent": self.parent,
            "children": [ child.name for child in self.children ],
            "files": [ file.name for file in self.files ],
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "users_with_rights": [ user.name for user in self.users_with_rights ]
        })

    def has_child_with(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

    def update_size(self, size):
        self.size += size

    def remove(self):
        for user in self.users_with_rights:
            user.directory_rights.remove(self)

        # Recursively removes all children
        # and also removes the user rights
        for child in self.children:
            child.remove()

        super(Directory, self).remove()

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