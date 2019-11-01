import os

from flask import jsonify, g, request, url_for, current_app, send_from_directory
from werkzeug import secure_filename

from . import controllers

from .authentication import auth
from .statuscodes import bad_request, already_exists, success, not_found
from ..models import Image, Video


@auth.login_required
@controllers.route("/filesystem/directories/list/", methods=["GET"])
def get_all_directories():
    directories = []
    for dirname in os.walk(current_app.config["BASEPATH"]):
        directories.append(dirname[0])
    return jsonify({"directories": directories})

# @auth.login_required
# @controllers.route("/filesystem/<directory>/", methods=["GET"])
# def get_files_in_directory(directory):
#     if directory and not directory.startswith("/"):
#         fullpath = os.path.join(current_app.config["BASEPATH"], directory)
#         if os.path.exists(fullpath):
#             return jsonify({"directories": os.listdir(fullpath)})
#         else:
#             return not_found("The directory does not exist.")
#     else:
#         return bad_request("No valid directory given")

@auth.login_required
@controllers.route("/filesystem/root/", methods=["GET"])
def get_directories_in_root():
    fullpath = os.path.join(current_app.config["BASEPATH"])
    if os.path.exists(fullpath):
        return jsonify({"directories": os.listdir(fullpath)})
    else: 
        return not_found("Root directory could not be found. Must check")

@auth.login_required
@controllers.route("/filesystem/image/<directory>/<name>/", methods=["GET"])
def get_image_in_directory(directory, name):
    image = Image.query.filter_by(directory=directory, name=name).first()
    if image:
        abspath = os.path.join(os.path.dirname(current_app.root_path), current_app.config["BASEPATH"])
        fullpath = os.path.join(abspath, directory)
        return send_from_directory(fullpath, image.name, as_attachment=True)
    return not_found("The image could not be found")

@auth.login_required
@controllers.route("/filesystem/video/<directory>/", methods=["GET"])
def get_video_in_directory(directory):
    _directory = directory.split("/")[-1:].join("/")
    print(_directory)
    name = directory.split("/")[:-1]
    print(name)
    video = Video.query.filter_by(directory=_directory, name=name).first()
    if video:
        abspath = os.path.join(os.path.dirname(current_app.root_path), current_app.config["BASEPATH"])
        fullpath = os.path.join(abspath, directory)
        return send_from_directory(fullpath, video.name, as_attachment=True)
    return not_found("The video could not be found")


"""
NEW IMPLEMENTATION
"""

@auth.login_required
@controllers.route("/filesystem/", methods=["POST"])
def get_files_in_directory():
    if request.method == "POST":
        directory = request.json.get("directory")
        
        if not directory.startswith("/"):
            fullpath = os.path.join(current_app.config["BASEPATH"], directory)
            if os.path.exists(fullpath):
                return jsonify({"directories": os.listdir(fullpath)})
            else:
                return not_found("The directory does not exist.")
        else:
            return bad_request("No valid directory given")

@auth.login_required
@controllers.route("/filesystem/image-list/", methods=["GET"])
def get_image_url_list():
    fullpath = os.path.join(current_app.config["BASEPATH"], "ios/photos/")
    amount = int(request.args.get("amount"))
    
    if os.path.exists(fullpath):
        image_urls = os.listdir(fullpath)

        if len(image_urls) > amount:
            image_urls = image_urls[:amount]
        
        images = []
        for image_url in image_urls:
            images.append(
                {
                    "image_url": image_url, 
                    "size": os.path.getsize(os.path.join(fullpath, image_url))
                })
        return jsonify(images)
    return not_found("The photos directory does not exist.")


@auth.login_required
@controllers.route("/filesystem/image/<path:filename>", methods=["GET"])
def download_image(filename):
    abspath = os.path.join(os.path.dirname(current_app.root_path), current_app.config["BASEPATH"])
    fullpath = os.path.join(abspath, "ios/photos/")

    if os.path.exists(fullpath):
        return send_from_directory(fullpath, filename, as_attachment=True)
    return not_found("URL Not Found")