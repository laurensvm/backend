import uuid
from flask import current_app

from ..utils import join
from .. import db
from .directory import Directory


class LocationMixin(object):
    latitude = db.Column(db.Float, default=None, nullable=True)
    longitude = db.Column(db.Float, default=None, nullable=True)

    def location_json(self):
        return {
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            }
        }


class AssetMixin(object):
    device = db.Column(db.String(30), nullable=True)
    resolution = db.Column(db.Integer, nullable=True)
    thumbnail_path = db.Column(db.String(512), nullable=True)
    local_id = db.Column(db.String(256), index=True)

    def asset_json(self):
        return {
            "device": self.device,
            "resolution": self.resolution,
            "local_identifier": self.local_id
        }

    def generate_thumbnail_path(self):
        thumbnail = Directory.get_thumbnail_directory()
        name = ".".join([str(uuid.uuid1()), "jpg"])
        return join(thumbnail.internal_path, name)

