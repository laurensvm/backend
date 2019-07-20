import os

from flask import jsonify, g, request, url_for, current_app
from werkzeug import secure_filename

from . import api
from .authentication import auth
from .statuscodes import bad_request, already_exists, success, not_found
from ..models import Video
from .. import db

@auth.login_required
@api.route("/video/", methods=["GET"])
def get_all_videos():
    videos = Video.query.limit(20).all()
    return jsonify({'videos': [video.to_json() for video in videos]}) 

@auth.login_required
@api.route("/video/add/", methods=["POST"])
def add_video():
    if 'file' in request.files:
        f = request.files["file"]
        directory = request.form["directory"]
        filename = secure_filename(f.filename)

        if Video.exists(directory, filename):
            return already_exists("This video with the path already exists")
        
        video = Video.from_file_and_directory(directory, filename)
        video.user = g.current_user

        db.session.add(video)
        db.session.commit()
        
        video.save(f)

        return success("Video successfully uploaded")
    else:
        return bad_request("Something went wrong with the data transmission")

@auth.login_required
@api.route("/video/directory/<directory>/", methods=["GET"])
def get_videos_in_directory(directory):
    videos = Video.query.filter_by(directory=directory).all()
    if videos:
        return jsonify({"videos": [video.to_json() for video in videos]})
    return not_found("No videos could be found in directory: {dir}".format(dir=directory))

@auth.login_required
@api.route("/video/<int:id>/", methods=["GET"])
def get_video_by_id(id):
    video = Video.query.filter_by(id=id).first()
    if video:
        return jsonify({"video": video.to_json()})
    return not_found("Video with id: {id} could not be found.".format(id=id))

@auth.login_required
@api.route("/video/name/<name>/", methods=["GET"])
def get_videos_by_name(name):
    videos = Video.query.filter_by(name=name).all()
    if videos:
        return jsonify({"videos": [video.to_json() for video in videos]})
    return not_found("No videos with name: {name} could be found.".format(name=name))