from flask import jsonify, g, request, send_from_directory

from . import files
from ..authentication import auth
from ..statuscodes import bad_request, not_found, unauthorized, success
from ...models import File, Directory, Type
from ...exceptions import IOException


@files.route("/", methods=["POST"])
@auth.login_required
def get_file_by_path():
    path = request.json.get("path")

    f = File.query.filter_by(path=path).first()
    if not f:
        return not_found("File with path {0} is not found".format(path))

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return jsonify(f.json())

@files.route("/<int:id>/", methods=["GET"])
@auth.login_required
def get_file_by_id(id):
    f = File.query.filter_by(id=id).first()

    if not f:
        return not_found("File was not found")

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return jsonify(f.json())


@files.route("/<string:name>/", methods=["GET"])
@auth.login_required
def get_files_with_name(name):
    files = File.query.filter_by(name=name)

    files_with_rights = []
    for file in files:
        if g.current_user in file.directory.users_with_rights:
            files_with_rights.append(file)

    return jsonify({'files': [ f.json() for f in files_with_rights ]})


@files.route("/directory/", methods=["POST"])
@auth.login_required
def get_files_in_directory():
    path = request.json.get("path") or request.json.get("directory")
    if not path:
        return bad_request("No valid directory was given")

    d = Directory.query.filter_by(path=path).first()
    if not d:
        return not_found("Directory was not found")


    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [ file.json() for file in d.files ]})


@files.route("/directory/<string:name>/", methods=["GET"])
@auth.login_required
def get_files_in_directory_with_name(name):
    d = Directory.query.filter_by(name=name).first()
    if not d:
        return not_found("Directory was not found")


    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [ file.json() for file in d.files ]})


@files.route("/directory/<int:id>/", methods=["GET"])
@auth.login_required
def get_files_in_directory_with_id(id):
    d = Directory.query.filter_by(id=id).first()
    if not d:
        return not_found("Directory was not found")


    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [ file.json() for file in d.files ]})


@files.route("/<int:id>/delete/", methods=["GET"])
@auth.login_required
def delete_file(id):
    if not g.current_user.admin:
        return unauthorized()

    f = File.get_by_id(id)

    if not f:
        return not_found("File not found")

    try:
        f.remove()
    except IOException as e:
        return jsonify(e.json())

    return success("File successfully deleted")


@files.route("/<int:id>/rename/", methods=["POST"])
@auth.login_required
def rename_file(id):
    if not g.current_user.admin:
        return unauthorized()

    name = request.json.get("name")

    if not name:
        return bad_request("No valid name given")

    f = File.get_by_id(id)

    if not f:
        return not_found("Directory is not found")

    try:
        f.rename(name)
    except IOException as e:
        return jsonify(e.json())

    return success("File id {file} renamed to {name}".format(
        file=f.id,
        name=f.name
    ))

########################### SENDING FILES ###########################

@files.route("/send/<int:id>/", methods=["GET"])
@auth.login_required
def send_file_by_id(id):
    f = File.get_by_id(id)

    if not f:
        return not_found("File was not found")

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return send_from_directory(f.directory.path, f.name, as_attachment=True)

@files.route("/send/", methods=["POST"])
@auth.login_required
def send_file_by_path():
    path = request.json.get("path")

    f = File.get_by_path(path)
    if not f:
        return not_found("File with path {0} is not found".format(path))

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return send_from_directory(f.directory.path, f.name, as_attachment=True)


@files.route("/upload/", methods=["POST"])
@auth.login_required
def upload_file():
    if not 'file' in request.files:
        return bad_request("No file is sent in this request")

    file = request.files.get("file") or None
    type = request.form.get("type") or None
    directory_id = request.form.get("directory_id") or None
    description = request.form.get("description") or None

    if not file:
        return bad_request("No file sent")


    if type in Type.values():
        if type in [Type.video.value, Type.image.value]:
            return bad_request("Please use the endpoint for {0}".format(type))
        type = Type[type]
    else:
        type = Type.default

    d = Directory.get_by_id(directory_id)

    if not d:
        return not_found("Directory does not exist")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    f = File(
        type=type,
        name=file.filename,
        directory=d,
        user=g.current_user
    )

    if description:
        f.description = description

    try:
        f.save(file)
    except IOException as e:
        return jsonify(e.json())

    return success("File successfully uploaded.")
