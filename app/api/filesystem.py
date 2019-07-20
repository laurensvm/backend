import os

from flask import jsonify, g, request, url_for, current_app, send_from_directory
from werkzeug import secure_filename

from . import api

from .authentication import auth
from .statuscodes import bad_request, already_exists, success, not_found
from ..models import Image, Video


@auth.login_required
@api.route("/filesystem/directories/list/", methods=["GET"])
def get_all_directories():
    directories = []
    for dirname in os.walk(current_app.config["BASEPATH"]):
        directories.append(dirname[0])
    return jsonify({"directories": directories})

@auth.login_required
@api.route("/filesystem/<directory>/", methods=["GET"])
def get_files_in_directory(directory):
    if directory and not directory.startswith("/"):
        fullpath = os.path.join(current_app.config["BASEPATH"], directory)
        print(fullpath)
        if os.path.exists(fullpath):
            return jsonify({"contents": os.listdir(fullpath)})
        else:
            return not_found("The directory does not exist.")
    else:
        return bad_request("No valid directory given")

@auth.login_required
@api.route("/filesystem/image/<directory>/<name>/", methods=["GET"])
def get_image_in_directory(directory, name):
    image = Image.query.filter_by(directory=directory, name=name).first()
    if image:
        abspath = os.path.join(os.path.dirname(current_app.root_path), current_app.config["BASEPATH"])
        fullpath = os.path.join(abspath, directory)
        return send_from_directory(fullpath, image.name, as_attachment=True)
    return not_found("The image could not be found")

@auth.login_required
@api.route("/filesystem/video/<directory>/<name>/", methods=["GET"])
def get_video_in_directory(directory, name):
    video = Video.query.filter_by(directory=directory, name=name).first()
    if video:
        abspath = os.path.join(os.path.dirname(current_app.root_path), current_app.config["BASEPATH"])
        fullpath = os.path.join(abspath, directory)
        return send_from_directory(fullpath, video.name, as_attachment=True)
    return not_found("The video could not be found")
