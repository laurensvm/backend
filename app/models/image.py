import uuid

from PIL import Image
from flask import current_app

from .file import File, Type, Directory
from .base import LocationMixin, AssetMixin

from ..utils import join


class Image(AssetMixin, LocationMixin, File):
    __tablename__ = "image"

    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
        self.type = Type.image
        self.thumbnail_path = self.generate_thumbnail_path()

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def generate_thumbnail_path(self):
        thumbnail = Directory.query.filter_by(name=current_app.config["THUMBNAIL_FOLDER"]).first()
        return join(thumbnail.internal_path, uuid.uuid1())

    def json(self):
        json = super(Image, self).json()
        json.update(super(Image, self).location_json())
        json.update(super(Image, self).asset_json())
        return json


    def save(self, f):
        super(Image, self).save(f)

        im = Image.open(self.internal_path)
        im.thumbnail(current_app.config["THUMBNAIL_IMAGE_QUALITY"])
        im.save(self.thumbnail_path)




