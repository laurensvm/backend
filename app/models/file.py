import enum
from sqlalchemy import and_

from .. import db
from ..exceptions import IOException
from ..utils import join, path_exists, remove, move, secure_filename, size
from .base import Base
from .user import User
from .directory import Directory

class Type(enum.Enum):
    pdf = "pdf"
    image = "image"
    video = "video"
    txt = "txt"
    default = "unknown"

    @property
    def values(self):
        return [type.value for type in Type]


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
        self.name = secure_filename(self.name)
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

    def move(self, destination):
        d = Directory.query.filter_by(path=destination).first()

        if not d:
            raise IOException(
                IOException.Type.path_does_not_exist,
                "Directory with destination path does not exist. Please create the directory first."
            )

        self.directory.update_size(self.size, increment=False)
        self.directory.files.remove(self)

        dest_path = join(self.path, self.name)
        move(self.path, dest_path)

        self.directory = d
        self.directory_id = d.id

        d.files.append(self)

        pass


    def save(self, f):
        if not path_exists(self.directory.path):
            raise IOException(IOException.Type.path_does_not_exist)

        if not self.user in self.directory.users_with_rights:
            raise IOException(IOException.Type.insufficient_rights)

        if path_exists(self.path):
            raise IOException(IOException.Type.path_already_exists)

        f.save(self.path)

        if self.size == None:
            self.size = size(self.path)

        super(File, self).save()
