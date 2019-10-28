import os

from flask import current_app, g
from datetime import datetime

from .. import db
from ..exceptions import ValidationError
from . import User



class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    directory = db.Column(db.String(256))
    filepath = db.Column(db.String(256), unique=True, index=True)
    format = db.Column(db.String(16), default=None, nullable=True)
    latitude = db.Column(db.Float, default=None, nullable=True)
    longitude = db.Column(db.Float, default=None, nullable=True)
    size = db.Column(db.Integer, default=None, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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

    def save(self, f):
        # find directory and save with image.directory
        full_filepath = os.path.join(current_app.config["BASEPATH"], self.filepath)
        if os.path.exists(full_filepath):
            raise Exception("Cannot save image. The filepath already exists")
        os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
        f.save(full_filepath)

    @staticmethod
    def from_file_and_directory(directory, filename):
        if directory is None:
            directory = "/"
        if filename is None:
            raise ValidationError("Image does not have a name")

        image = Image(name=filename, directory=directory, user_id=1)
        image.filepath = os.path.join(directory, filename)
        return image

    @staticmethod
    def exists(directory, filename):
        if Image.query.filter_by(filepath=os.path.join(directory, filename)).first():
            return True
        return False