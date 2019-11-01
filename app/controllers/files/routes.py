from flask import jsonify, g, request

from . import files
from ..authentication import auth
from ..statuscodes import bad_request, not_found, unauthorized
from ...models import File, Directory

@auth.login_required
@files.route("/", methods=["POST"])
def get_files_in_directory():
    path = request.json.get("path") or request.json.get("directory")
    if not path:
        return bad_request("No valid directory was given")

    d = Directory.query.filter_by(path=path).first()
    if not d:
        return not_found("Directory was not found")


    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [file.json() for file in d.files ]})

@auth.login_required
@files.route("/<int:id/", methods=["GET"])
def get_file_by_id(id):
    f = File.query.filter_by(id=id).first()

    if not f:
        return not_found("File was not found")

    if not g.current_user in f.directory.users_with_rights:
        return unauthorized()

    return jsonify(f.json())