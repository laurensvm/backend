from flask import jsonify, g, request

from . import directory
from ..authentication import auth
from ..statuscodes import unauthorized, success, bad_request, not_found
from ...utils import join
from ...models import Directory

@directory.before_app_first_request
def create_root_directory():
    root = Directory.query.filter_by(path="/").first()
    if not root:
        Directory.create_root()


@directory.route("/", methods=["POST"])
@auth.login_required
def get_children():
    name = request.json.get("name")
    path = request.json.get("path")

    if not path and not name:
        return bad_request("No valid name or path given. Please use a path to combat ambiguity.")

    d = Directory.find_by_name_and_path(name, path)
    if not d:
        return not_found("Directory not found")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({ "children": [child.name for child in d.children ] })

@directory.route("/create/", methods=["POST"])
@auth.login_required
def create_directory():
    if not g.current_user.admin:
        return unauthorized()


    name = request.json.get("name")
    path = request.json.get("path")

    parent = Directory.query.filter_by(path=path).first()

    if not parent:
        return bad_request("Directory with path does not exist")

    if parent.has_child_with_name(name):
        return bad_request("Directory with path {0} and name {1} already exists"
                           .format(path, name))
    # Create directory
    d = Directory(
        parent_id=parent.id,
        name=name,
        path=join(path, name))
    d.users_with_rights.append(g.current_user)

    d.save()

    return success("Directory successfully created")


@directory.route("/rights/", methods=["POST"])
@auth.login_required
def get_directory_rights():
    if not g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")
    directory = Directory.query.filter_by(path=path).first()
    return jsonify({'users': [ user.username for user in directory.users_with_rights ]})


@directory.route('/delete/', methods=["POST"])
@auth.login_required
def delete_directory():
    if g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")

    d = Directory.query.filter_by(path=path).first()
    if not d:
        return bad_request("Directory does not exist")

    d.remove()
    return success("Directory with path: {0} successfully deleted".format(path))
