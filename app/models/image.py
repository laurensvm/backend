import os

from flask import current_app, g

from .. import db
from ..exceptions import ValidationError
from .file import File
from .base import LocationMixin



class Image(LocationMixin, File):
    __tablename__ = "image"
    resolution = db.Column(db.Integer, default=None, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def to_json(self):
        json = super(Image, self).json()
        json = json.update(super(LocationMixin, self).json())
        return json.update({
            "resolution": self.resolution
        })



    # def save(self, f):
    #     # find directory and save with image.directory
    #     full_filepath = os.path.join(current_app.config["BASEPATH"], self.filepath)
    #     if os.path.exists(full_filepath):
    #         raise Exception("Cannot save image. The filepath already exists")
    #     os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
    #     f.save(full_filepath)
    #
    # @staticmethod
    # def from_file_and_directory(directory, filename):
    #     if directory is None:
    #         directory = "/"
    #     if filename is None:
    #         raise ValidationError("Image does not have a name")
    #
    #     image = Image(name=filename, directory=directory, user_id=1)
    #     # image.filepath = os.path.join(directory, filename)
    #     return image
    #
    # @staticmethod
    # def exists(directory, filename):
    #     if Image.query.filter_by(filepath=os.path.join(directory, filename)).first():
    #         return True
    #     return False