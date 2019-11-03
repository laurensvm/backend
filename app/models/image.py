import uuid

from PIL import Image as Im
from flask import current_app
from sqlalchemy import event, desc
from collections import defaultdict

from .file import File, Type, Directory
from .mixins import LocationMixin, AssetMixin

from .. import db


class Image(AssetMixin, LocationMixin, File):
    __tablename__ = "image"
    id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)


    def __init__(self, **kwargs):
        self.type = Type.image
        self.thumbnail_path = self.generate_thumbnail_path()
        super(Image, self).__init__(**kwargs)

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

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

    @staticmethod
    def get_by_id(id):
        return Image.query.filter_by(id=id).first()

    @staticmethod
    def get_latest(amount):
        return Image.query.order_by(desc(Image.timestamp)).limit(amount).all()


@event.listens_for(Image, 'mapper_configured')
def receive_mapper_configured(mapper, class_):
    mapper.polymorphic_map = defaultdict(lambda: mapper, mapper.polymorphic_map)

    # to prevent 'incompatible polymorphic identity' warning, not mandatory
    mapper._validate_polymorphic_identity = None