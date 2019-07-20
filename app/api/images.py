import os

from flask import jsonify, g, request, url_for, current_app
from werkzeug import secure_filename

from . import api
from .authentication import auth
from .statuscodes import bad_request, already_exists, success, not_found
from ..models import Image
from ..utilities import process_image, save_image
from .. import db

@auth.login_required
@api.route("/image/", methods=["GET"])
def get_all_images():
    images = Image.query.limit(20).all()
    return jsonify({'images': [image.to_json() for image in images]}) 

@auth.login_required
@api.route("/image/add/", methods=["POST"])
def add_image():
    if 'file' in request.files:
        f = request.files["file"]
        directory = request.form["directory"]
        filename = secure_filename(f.filename)

        if Image.exists(directory, filename):
            return already_exists("This image with the path already exists")

        # Fix
        size, format = process_image(f)
        
        image = Image.from_file_and_directory(directory, filename)
        image.user = g.current_user
        image.size = size
        image.format = format

        db.session.add(image)
        db.session.commit()
        
        # find directory and save with image.directory
        full_filepath = os.path.join(current_app.config["BASEPATH"], image.filepath)
        if os.path.exists(full_filepath):
            raise Exception("Cannot save image. The filepath already exists")
        os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
        f.save(full_filepath)

        return success("Image successfully uploaded")
    else:
        return bad_request("Something went wrong with the data transmission")

@auth.login_required
@api.route("/image/directory/<directory>/", methods=["GET"])
def get_images_in_directory(directory):
    images = Image.query.filter_by(directory=directory).all()
    if images:
        return jsonify({"images": [image.to_json() for image in images]})
    return not_found("No images could be found in directory: {dir}".format(dir=directory))

@auth.login_required
@api.route("/image/<int:id>/", methods=["GET"])
def get_image_by_id(id):
    image = Image.query.filter_by(id=id).first()
    if image:
        return jsonify({"image": image.to_json()})
    return not_found("Image with id: {id} could not be found.".format(id=id))

@auth.login_required
@api.route("/image/name/<name>/", methods=["GET"])
def get_images_by_name(name):
    images = Image.query.filter_by(name=name).all()
    if images:
        return jsonify({"images": [image.to_json() for image in images]})
    return not_found("No images with name: {name} could be found.".format(name=name))