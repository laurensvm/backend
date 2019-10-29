import os
import enum
from .. import db

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
    user = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'file',
        'polymorphic_on': type
    }

    @property
    def path(self):
        return os.path.join(self.directory.path, self.name)

    @staticmethod
    def make_filename_safe(name):
        return "".join([c for c in name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)
        self.name = File.make_filename_safe(self.name)
        self.directory.update_size(self.size)

    def json(self):
        json = super(File, self).json()
        return json.update({
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "size": self.size,
            "directory": self.directory,
            "user": self.user
        })