from datetime import datetime

from .. import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def json(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "updated": self.updated
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def commit(self):
        db.session.commit()


class Link(db.Model):
    __tablename__ = "link"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    directory_id = db.Column(db.Integer, db.ForeignKey("directory.id"), primary_key=True)

