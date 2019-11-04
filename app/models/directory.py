from flask import current_app

from .. import db
from . import *
from .base import Base
from ..utils import remove_dir, join, secure_filename, makedir, rename
from ..exceptions import IOException

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
        self.path = Directory.generate_path(self.parent_id, self.name)
        self.internal_path = Directory.generate_internal_path(self.path)

        if self.parent and self.size != 0:
            self.parent.update_size(self.size)

        makedir(self.internal_path)

        db.session.flush()


    def __repr__(self):
        return 'Directory {0}'.format(self.id)

    def __str__(self):
        return 'Directory {0}'.format(self.id)

    def json(self):
        json = super(Directory, self).json()
        json.update({
            "parent_id": self.parent_id,
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

        # Recursively move up the directory tree to update the size
        if self.parent:
            self.parent.update_size(self.size, increment=increment)

    def rename(self, name):
        old_path = self.internal_path

        name = secure_filename(name)
        new_path = Directory.generate_path(self.parent_id, name)

        d = Directory.get_by_path(new_path)
        if d:
            raise IOException(IOException.Type.path_already_exists)


        with db.session.no_autoflush:
            self.name = name
            self.path = Directory.generate_path(self.parent_id, self.name)
            self.internal_path = Directory.generate_internal_path(self.path)

        rename(old_path, self.internal_path)
        self.commit()

    def remove(self):
        self.users_with_rights = []

        if self.parent:
            self.parent.update_size(self.size, increment=False)

        # Recursively removes all children
        # and corresponding user rights
        for child in self.children:
            child.remove()

        # Also remove all the files
        for file in self.files:
            file.remove()

        try:
            remove_dir(self.internal_path)
        except FileNotFoundError:
            raise IOException(IOException.Type.file_not_found)

        super(Directory, self).remove()


    @staticmethod
    def exists(path):
        if Directory.query.filter_by(path=path).first():
            return True
        return False

    @staticmethod
    def get_abspath():
        return current_app.config["BASEPATH"]

    @staticmethod
    def create_root():
        root = current_app.config["ROOT_FOLDER"]
        d = Directory(parent_id=None, name=root, path=root)

        admins = User.query.filter_by(admin=True)
        d.users_with_rights.extend(admins)
        d.save()

    @staticmethod
    def generate_path(parent, name):

        if isinstance(parent, int):
            parent = Directory.get_by_id(parent)

        if not parent:
            return secure_filename(name)

        if name == current_app.config["ROOT_FOLDER"]\
                or name == current_app.config["THUMBNAIL_FOLDER"]:
            return secure_filename(name)

        return join(parent.path, secure_filename(name))

    @staticmethod
    def generate_internal_path(path):
        return join(Directory.get_abspath(), path)

    @staticmethod
    def create_thumbnails():
        name = current_app.config["THUMBNAIL_FOLDER"]
        d = Directory(parent_id=None, name=name, path=name)

        admins = User.query.filter_by(admin=True)
        d.users_with_rights.extend(admins)
        d.save()

    @staticmethod
    def get_thumbnail_directory():
        return Directory.query.filter_by(name=current_app.config["THUMBNAIL_FOLDER"]).first()

    @staticmethod
    def get_root_directory():
        return Directory.query.filter_by(name=current_app.config["ROOT_FOLDER"]).first()

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

    @staticmethod
    def add_user_to_thumbnails(user):
        d = Directory.get_by_name(current_app.config["THUMBNAIL_FOLDER"]).first()
        d.users_with_rights.add(user)