import enum
from sqlalchemy import and_
from werkzeug.utils import secure_filename

from .. import db
from ..utils import join, path_exists, remove, move
from .base import Base
from .user import User
from .directory import Directory

class Type(enum.Enum):
    pdf = "pdf"
    image = "image"
    video = "video"
    txt = "txt"
    default = "unknown"

class File(Base):
    __tablename__ = 'file'
    type = db.Column(db.Enum(Type), default=Type.default)
    size = db.Column(db.BigInteger, nullable=True)
    name = db.Column(db.String(256), index=True)
    description = db.Column(db.String(4096), nullable=True)
    directory = db.relationship(Directory, back_populates="files")
    directory_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=False)
    user = db.relationship(User, back_populates="files")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'file',
        'polymorphic_on': type
    }

    @property
    def path(self):
        return join(self.directory.path, self.name)

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)
        self.name = File.secure_filename(self.name)
        self.directory.update_size(self.size)

    def remove(self):
        self.directory.update_size(self.size, increment=False)
        self.directory.files.remove(self)
        remove(self.path)
        super(File, self).remove()

    def json(self):
        json = super(File, self).json()
        json.update({
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "size": self.size,
            "directory": self.directory,
            "user": self.user
        })
        return json

    @staticmethod
    def exists(path, name):
        return File.query.join(Directory).filter(
            and_(Directory.path == path, File.name == name)
        ).first() is not None

    @staticmethod
    def secure_filename(name):
        return secure_filename(name)

    def save(self, f):
        if not path_exists(self.directory.path):
            raise Exception("Path does not exist")

        if not self.user in self.directory.users_with_rights:
            raise Exception("User does not have rights to perform IO operations in this directory")

        if path_exists(self.path):
            raise Exception("Cannot save image. The file path already exists")

        f.save(self.path)

        super(File, self).save()
