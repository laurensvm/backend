import os

from flask import current_app, g
from app.exceptions import ValidationError
from datetime import datetime

from .. import db
from . import User

class Video(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    directory = db.Column(db.String(256))
    filepath = db.Column(db.String(256), unique=True, index=True)
    format = db.Column(db.String(16), default=None, nullable=True)
    latitude = db.Column(db.Float, default=None, nullable=True)
    longitude = db.Column(db.Float, default=None, nullable=True)
    size = db.Column(db.Integer, default=None, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)

    def to_json(self):
        json_post = {
            "id": self.id,
            "name": self.name,
            "directory": self.directory,
            "format": self.format,
            "size": self.size,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "filepath": self.filepath,
            "timestamp": self.timestamp,
            "user_id": self.user_id
        }
        return json_post


    @staticmethod
    def from_file_and_directory(directory, filename):
        if directory is None:
            directory = "/"
        if filename is None:
            raise ValidationError("Video does not have a name")
        video = Video(name=filename, directory=directory, user_id=g.current_user.id)
        video.filepath = os.path.join(directory, filename)
        return video

    def save(self, f):
        # find directory and save with image.directory
        full_filepath = os.path.join(current_app.config["BASEPATH"], self.filepath)
        if os.path.exists(full_filepath):
            raise Exception("Cannot save video. The filepath already exists")
        os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
        f.save(full_filepath)

    @staticmethod
    def exists(directory, filename):
        if Video.query.filter_by(filepath=os.path.join(directory, filename)).first():
            return True
        return False