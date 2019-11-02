from flask import jsonify, g, request, send_file
from sqlalchemy import desc

from . import images
from ..authentication import auth
from ..statuscodes import bad_request, not_found, unauthorized, success
from ...models import Image, Type, Directory
from ...exceptions import IOException


@images.route("/", methods=["GET"])
@auth.login_required
def get_latest_images():
    try:
        amount = int(request.args.get("amount")) or 30
    except ValueError as e:
        return bad_request("Could not convert amount to integer")

    images = Image.query.order_by(desc(Image.timestamp)).limit(amount).all()

    for image in images:
        if not g.current_user in image.directory.users_with_rights:
            images.remove(image)

    return jsonify({'images': [image.json() for image in images]})

@images.route("/thumbnail/<int:id>/", methods=["GET"])
@auth.login_required
def get_thumbnail_image(id):
    image = Image.get_by_id(id)

    if not g.current_user in image.directory.users_with_rights:
        return unauthorized()

    return send_file(image.thumbnail_path)


@images.route("/upload/", methods=["POST"])
@auth.login_required
def upload_file():
    if not 'file' in request.files:
        return bad_request("No file is sent in this request")

    file = request.files.get("file") or None
    type = request.form.get("type") or None
    directory_id = request.form.get("directory_id") or None
    description = request.form.get("description") or None
    latitude = request.form.get("latitude") or None
    longitude = request.form.get("longitude") or None
    device = request.form.get("device") or None
    resolution = request.form.get("resolution") or None
    local_id = request.form.get("local_identifier")

    if not file:
        return bad_request("No file sent")


    if type not in [Type.image, None]:
        return bad_request("Please use the endpoint for {0}".format(type))

    d = Directory.get_by_id(directory_id)

    if not d:
        return not_found("Directory does not exist")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    im = Image(
        name=file.filename,
        directory=d,
        user=g.current_user,
        latitude=latitude,
        longitude=longitude,
        device=device,
        resolution=resolution,
    )

    if description:
        im.description = description

    if local_id:
        im.local_id = local_id

    try:
        im.save(file)
    except IOException as e:
        return jsonify(e.json())

    return success("Image successfully uploaded.")

@images.route("/download/<int:id>/", methods=["GET"])
@auth.login_required
def download_image(id):
    im = Image.get_by_id(id)

    if not im:
        return not_found("Image with id {0} not found".format(id))

    if not g.current_user in im.directory.users_with_rights:
        return unauthorized()

    return send_file(im.internal_path)


@images.route("/<int:id>/", methods=["GET"])
@auth.login_required
def get_image(id):
    im = Image.get_by_id(id)

    if not im:
        return not_found("Image with id {0} not found".format(id))

    if not g.current_user in im.directory.users_with_rights:
        return unauthorized()

    return jsonify(im.json())