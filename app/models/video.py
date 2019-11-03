from sqlalchemy import event
from collections import defaultdict

from .mixins import LocationMixin, AssetMixin
from .file import Type, File
from .. import db

class Video(AssetMixin, LocationMixin, File):
    __tablename__ = "video"
    id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)
    length = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'video',
    }

    def __init__(self, **kwargs):
        super(Video, self).__init__(**kwargs)
        self.type = Type.video


    def json(self):
        json = super(Video, self).json()
        json.update(super(Video, self).location_json())
        json.update(super(Video, self).asset_json())
        json.update({
            "length": self.length
        })
        return json

    def json_length(self):
        return {
            "length": self.length
        }

    def save_thumbnail(self, im):
        self.thumbnail_path = self.generate_thumbnail_path()
        im.save(self.thumbnail_path)



@event.listens_for(Video, 'mapper_configured')
def receive_mapper_configured(mapper, class_):
    mapper.polymorphic_map = defaultdict(lambda: mapper, mapper.polymorphic_map)

    # to prevent 'incompatible polymorphic identity' warning, not mandatory
    mapper._validate_polymorphic_identity = None