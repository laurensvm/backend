import os

from flask import current_app, g
from ..exceptions import ValidationError
from datetime import datetime

from .. import db
from .base import Base

class Video(Base):
    __tablename__ = "video"
    # latitude = db.Column(db.Float, default=None, nullable=True)
    # longitude = db.Column(db.Float, default=None, nullable=True)
    # # quality / resolution

    # def __init__(self, **kwargs):
    #     super(Image, self).__init__(**kwargs)
    #     self.type = Type.video
    #
    # def to_json(self):
    #     json_post = {
    #         "id": self.id,
    #         "name": self.name,
    #         "directory": self.directory,
    #         "format": self.format,
    #         "size": self.size,
    #         "latitude": self.latitude,
    #         "longitude": self.longitude,
    #         "filepath": self.filepath,
    #         "timestamp": self.timestamp,
    #         "user_id": self.user_id
    #     }
    #     return json_post
    #
    #
    # @staticmethod
    # def from_file_and_directory(directory, filename):
    #     if directory is None:
    #         directory = "/"
    #     if filename is None:
    #         raise ValidationError("Video does not have a name")
    #     video = Video(name=filename, directory=directory, user_id=g.current_user.id)
    #     video.filepath = os.path.join(directory, filename)
    #     return video
    #
    # def save(self, f):
    #     # find directory and save with image.directory
    #     full_filepath = os.path.join(current_app.config["BASEPATH"], self.filepath)
    #     if os.path.exists(full_filepath):
    #         raise Exception("Cannot save video. The filepath already exists")
    #     os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
    #     f.save(full_filepath)
    #
    # @staticmethod
    # def exists(directory, filename):
    #     if Video.query.filter_by(filepath=os.path.join(directory, filename)).first():
    #         return True
    #     return False