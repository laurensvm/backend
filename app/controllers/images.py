import os

from flask import jsonify, g, request, url_for, current_app
from werkzeug.utils import secure_filename

from . import controllers
from .authentication import auth
from .statuscodes import bad_request, already_exists, success, not_found, internal_error
from ..models import Image, User
from .. import db

@auth.login_required
@controllers.route("/image/", methods=["GET"])
def get_all_images():
    images = Image.query.limit(20).all()
    return jsonify({'images': [image.to_json() for image in images]}) 

@auth.login_required
@controllers.route("/image/add/", methods=["POST"])
def add_image():
    if 'file' in request.files:
        f = request.files["file"]
        directory = request.form["directory"]
        filename = secure_filename(f.filename)

        if Image.exists(directory, filename):
            return already_exists("This image with the path already exists")

        # Fix
        # size, format = process_image(f)
        
        image = Image.from_file_and_directory(directory, filename)
        image.user = User.query.filter_by(id=1).first()
        # image.size = size
        # image.format = format

        db.session.add(image)
        db.session.commit()

        try:
            image.save(f)
        except Exception as e:
            return internal_error("Cannot save image because it exists on the filesystem."
                                  + " Database and Filesystem are not synchronized. CRITICAL!")

        return success("Image successfully uploaded")
    else:
        return bad_request("Something went wrong with the data transmission")

@auth.login_required
@controllers.route("/image/directory/<directory>/", methods=["GET"])
def get_images_in_directory(directory):
    images = Image.query.filter_by(directory=directory).all()
    if images:
        return jsonify({"images": [image.to_json() for image in images]})
    return not_found("No images could be found in directory: {dir}".format(dir=directory))

@auth.login_required
@controllers.route("/image/<int:id>/", methods=["GET"])
def get_image_by_id(id):
    image = Image.query.filter_by(id=id).first()
    if image:
        return jsonify({"image": image.to_json()})
    return not_found("Image with id: {id} could not be found.".format(id=id))

@auth.login_required
@controllers.route("/image/name/<name>/", methods=["GET"])
def get_images_by_name(name):
    images = Image.query.filter_by(name=name).all()
    if images:
        return jsonify({"images": [image.to_json() for image in images]})
    return not_found("No images with name: {name} could be found.".format(name=name))