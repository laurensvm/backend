from datetime import datetime

from .. import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=db.func.now())

    def json(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "updates": self.updated
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(self):
        return Base.query.filter(id=id).first()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

class Link(db.Model):
    __tablename__ = "link"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    directory_id = db.Column(db.Integer, db.ForeignKey("directory.id"), primary_key=True)

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