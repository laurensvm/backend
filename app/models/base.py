from datetime import datetime

from .. import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=db.func.now())

