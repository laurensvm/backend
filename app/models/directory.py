from flask import current_app

from .. import db
from .base import Base
from .user import User
from ..utils import remove_dir, join, secure_filename, makedir

class Directory(Base):
    __tablename__ = "directory"
    parent_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=True)
    children = db.relationship("Directory", backref=db.backref('parent', remote_side='Directory.id'))
    files = db.relationship("File", back_populates="directory", cascade="all, delete, delete-orphan")
    name = db.Column(db.String(256), index=True)
    path = db.Column(db.String(256), unique=True, index=True)
    internal_path = db.Column(db.String(256), unique=True, index=True)
    size = db.Column(db.BigInteger, default=0)
    users_with_rights = db.relationship("User", secondary="link")

    def __init__(self, **kwargs):
        super(Directory, self).__init__(**kwargs)
        self.internal_path = join(current_app.config["BASEPATH"], self.path)
        makedir(self.internal_path)


    def __repr__(self):
        return 'Directory <{0}>'.format(self.path)

    def json(self):
        json = super(Directory, self).json()
        json.update({
            "parent": self.parent,
            "children": [ child.name for child in self.children ],
            "files": [ file.name for file in self.files ],
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "users_with_rights": [ user.username for user in self.users_with_rights ]
        })
        return json

    def has_child_with_name(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

    def update_size(self, size, increment=True):
        if increment:
            self.size += size
        else:
            self.size -= size

    def remove(self):
        for user in self.users_with_rights:
            user.directory_rights.remove(self)

        # Recursively removes all children
        # and corresponding user rights
        for child in self.children:
            child.remove()

        # Also remove all the files
        for file in self.files:
            file.remove()

        remove_dir(self.path)

        super(Directory, self).remove()


    @staticmethod
    def exists(path):
        if Directory.query.filter_by(path=path).first():
            return True
        return False

    # @staticmethod
    # def get_abspath():
        # return

    @staticmethod
    def create_root():
        d = Directory(parent_id=None, name="root", path="root")

        admins = User.query.filter_by(admin=True)
        d.users_with_rights.extend(admins)
        d.save()

    @staticmethod
    def generate_path(parent, name):

        if isinstance(parent, int):
            parent = Directory.query.filter_by(id=parent).first()

        return join(parent.path, secure_filename(name))

    @staticmethod
    def create_thumbnails():
        name = current_app.config["THUMBNAIL_FOLDER"]
        root = Directory.query.filter_by(name="root").first()
        d = Directory(parent_id=root.id, name=name, path=Directory.generate_path(root, name))

        admins = User.query.filter_by(admin=True)
        d.users_with_rights.extend(admins)
        d.save()

    @staticmethod
    def get_by_path(path):
        return Directory.query.filter_by(path=path).first()

    @staticmethod
    def get_by_id(id):
        return Directory.query.filter_by(id=id).first()

    @staticmethod
    def get_by_name(name):
        return Directory.query.filter_by(name=name).first()

    @staticmethod
    def get_parent(path):
        d = Directory.get_by_path(path)
        if d:
            return d.parent
        return None