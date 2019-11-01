import os

from flask import current_app, g

from .. import db
from ..exceptions import ValidationError
from .file import File, Type
from .base import LocationMixin



class Image(LocationMixin, File):
    __tablename__ = "image"
    resolution = db.Column(db.Integer, default=None, nullable=True)

    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
        self.type = Type.image

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def json(self):
        json = super(Image, self).json()
        json.update(super(Image, self).location_json())
        json.update({
            "resolution": self.resolution
        })
        return json

    def remove(self):
        super(Image, self).remove()

