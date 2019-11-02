import uuid

from PIL import Image as Im
from flask import current_app
from sqlalchemy import event
from collections import defaultdict

from .file import File, Type, Directory
from .base import LocationMixin, AssetMixin

from ..utils import join


class Image(AssetMixin, LocationMixin, File):
    __tablename__ = "image"

    def __init__(self, **kwargs):
        self.type = Type.image
        self.thumbnail_path = self.generate_thumbnail_path()
        super(Image, self).__init__(**kwargs)

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def generate_thumbnail_path(self):
        thumbnail = Directory.query.filter_by(name=current_app.config["THUMBNAIL_FOLDER"]).first()
        name = ".".join([str(uuid.uuid1()), "jpg"])
        return join(thumbnail.internal_path, name)

    def json(self):
        json = super(Image, self).json()
        json.update(super(Image, self).location_json())
        json.update(super(Image, self).asset_json())
        return json


    def save(self, f):
        super(Image, self).save(f)

        im = Im.open(self.internal_path)
        im.thumbnail(current_app.config["THUMBNAIL_IMAGE_QUALITY"])
        im.save(self.thumbnail_path)


@event.listens_for(Image, 'mapper_configured')
def receive_mapper_configured(mapper, class_):
    mapper.polymorphic_map = defaultdict(lambda: mapper, mapper.polymorphic_map)

    # to prevent 'incompatible polymorphic identity' warning, not mandatory
    mapper._validate_polymorphic_identity = None