from flask import jsonify, g, request, send_from_directory

from . import files
from ..authentication import auth
from ..statuscodes import bad_request, not_found, unauthorized, success
from ...models import File, Directory, Type
from ...exceptions import IOException


@auth.login_required
@files.route("/", methods=["POST"])
def get_file_by_path():
    path = request.json.get("path")

    f = File.query.filter_by(path=path).first()
    if not f:
        return not_found("File with path {0} is not found".format(path))

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return jsonify(f.json())


@auth.login_required
@files.route("/files/", methods=["POST"])
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


@auth.login_required
@files.route("/<int:id/", methods=["GET"])
def get_file_by_id(id):
    f = File.query.filter_by(id=id).first()

    if not f:
        return not_found("File was not found")

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return jsonify(f.json())


@auth.login_required
@files.route("/<string:name>/", methods=["GET"])
def get_files_with_name(name):
    files = File.query.filter_by(name=name)

    files_with_rights = []
    for file in files:
        if g.current_user in file.directory.users_with_rights:
            files_with_rights.append(file)

    return jsonify({'files': [ f.json() for f in files_with_rights ]})


@auth.login_required
@files.route("/delete/<int:id>/", methods=["GET"])
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

########################### SENDING FILES ###########################
@auth.login_required
@files.route("/send/<int:id>/", methods=["GET"])
def send_file_by_id(id):
    f = File.get_by_id(id)

    if not f:
        return not_found("File was not found")

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return send_from_directory(f.directory.path, f.name, as_attachment=True)

@auth.login_required
@files.route("/send/", methods=["POST"])
def send_file_by_path():
    path = request.json.get("path")

    f = File.get_by_path(path)
    if not f:
        return not_found("File with path {0} is not found".format(path))

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return send_from_directory(f.directory.path, f.name, as_attachment=True)


@auth.login_required
@files.route("/upload/", methods=["POST"])
def upload_file():
    if not 'file' in request.files:
        return bad_request("No file is sent in this request")

    file = request.files["file"]
    type = request.form["type"]
    directory_id = request.form["directory_id"]
    description = request.form["description"]

    if type in Type.values:
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
        name=file.name,
        directory_id=d.id,
        user=g.current_user
    )

    if description:
        f.description = description

    try:
        f.save()
    except IOException as e:
        return jsonify(e.json())

    return success("File successfully uploaded.")
