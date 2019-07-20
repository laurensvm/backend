from flask import jsonify, g, request, url_for, current_app
from .. import db
from ..models import Track
from . import api
from .authentication import auth
from .statuscodes import already_exists

@api.route("/tracks/")
@auth.login_required
def get_all_tracks():
    tracks = Track.query.all()
    return jsonify({'tracks': [track.to_json() for track in tracks]}) 

@api.route("/tracks/add/", methods=["POST"])
@auth.login_required
def add_track():
    track = Track.from_json(request.json)
    if Track.exists(url):
        return already_exists("This url already exists")
    track.user = g.current_user
    db.session.add(track)
    db.session.commit()
    return jsonify(track.to_json(), 201)

@api.route("/")
@auth.login_required
def index():
    return "{user}".format(user=g.current_user)
