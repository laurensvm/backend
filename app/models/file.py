import enum
from os.path import join
from sqlalchemy import and_, event
from collections import defaultdict

from .. import db
from ..exceptions import IOException
from ..utils import path_exists, remove, move, secure_filename, size
from .base import Base
from .user import User
from .directory import Directory


class Type(enum.Enum):
    pdf = "pdf"
    image = "image"
    video = "video"
    txt = "txt"
    default = "unknown"

    @staticmethod
    def values():
        return [type.value for type in Type]

class File(Base):
    __tablename__ = 'file'
    type = db.Column(db.Enum(Type), default=Type.default)
    size = db.Column(db.BigInteger, nullable=True)
    name = db.Column(db.String(256), index=True)
    extension = db.Column(db.String(16))
    description = db.Column(db.String(4096), nullable=True)
    directory = db.relationship(Directory, back_populates="files")
    directory_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=False)
    user = db.relationship(User, back_populates="files")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'file',
        'polymorphic_on': type
    }

    def __repr__(self):
        return 'File <{0}>'.format(self.name)

    @property
    def internal_path(self):
        return join(self.directory.internal_path, ".".join([self.name, self.extension]))

    @property
    def path(self):
        return join(self.directory.path, ".".join([self.name, self.extension]))


    def __init__(self, **kwargs):
        self.name, self.extension = self.parse_name(kwargs.pop("name"))
        super(File, self).__init__(**kwargs)


    def parse_name(self, name_extension):
        name_ext_lst = name_extension.split(".")
        name = "".join(name_ext_lst[:-1])
        name = secure_filename(name)

        extension = name_ext_lst[-1]

        return name, extension


    def remove(self):
        remove(self.internal_path)

        with db.session.no_autoflush:
            self.user.files.remove(self)
            self.directory.update_size(self.size, increment=False)
            self.directory.files.remove(self)

        super(File, self).remove()


    @staticmethod
    def get_by_path(path):
        return File.query.filter_by(path=path).first()

    def json(self):
        json = super(File, self).json()
        json.update({
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "size": self.size,
            "directory": self.directory.path,
            "user": self.user.username
        })
        return json

    @staticmethod
    def exists(path, name):
        return File.query.join(Directory).filter(
            and_(Directory.path == path, File.name == name)
        ).first() is not None

    @staticmethod
    def get_by_id(id):
        return File.query.filter_by(id=id).first()

    # def move(self, destination):
    #     d = Directory.query.filter_by(path=destination).first()
    #
    #     if not d:
    #         raise IOException(
    #             IOException.Type.path_does_not_exist,
    #             "Directory with destination path does not exist. Please create the directory first."
    #         )
    #
    #     self.directory.update_size(self.size, increment=False)
    #     self.directory.files.remove(self)
    #
    #     dest_path = join(self.path, self.name)
    #     move(self.path, dest_path)
    #
    #     self.directory = d
    #     self.directory_id = d.id
    #
    #     d.files.append(self)
    #
    #     pass


    def save(self, f):
        if not path_exists(self.directory.internal_path):
            raise IOException(IOException.Type.path_does_not_exist)

        if not self.user in self.directory.users_with_rights:
            raise IOException(IOException.Type.insufficient_rights)

        if path_exists(self.internal_path):
            raise IOException(IOException.Type.path_already_exists)

        f.save(self.internal_path)

        if self.size == None:
            self.size = size(self.internal_path)

        self.directory.update_size(self.size)

        super(File, self).save()


@event.listens_for(File, 'mapper_configured')
def receive_mapper_configured(mapper, class_):
    mapper.polymorphic_map = defaultdict(lambda: mapper, mapper.polymorphic_map)

    # to prevent 'incompatible polymorphic identity' warning, not mandatory
    mapper._validate_polymorphic_identity = None