from flask import jsonify, g, request

from . import directories
from ..authentication import auth
from ..statuscodes import unauthorized, success, bad_request, not_found
from ...utils import join
from ...models import Directory

@directories.before_app_first_request
def create_root_directory():
    root = Directory.find_by_path("/")
    if not root:
        Directory.create_root()


@auth.login_required
@directories.route("/", methods=["GET", "POST"])
def get_children():
    if request.method == "POST":
        path = request.json.get("path")

        if not path:
            return bad_request("No valid path given.")

        d = Directory.get_by_path(path)
        if not d:
            return not_found("Directory not found")

        if not g.current_user in d.users_with_rights:
            return unauthorized()

        return jsonify({ "children": [child.name for child in d.children ] })

    else:
        directories = Directory.query.all()
        return jsonify({ "directories": [ directory.json() for directory in directories ] })


@auth.login_required
@directories.route("/get-id/", methods=["POST"])
def get_directory_id():
    path = request.json.get("path")

    if not path:
        return bad_request("No valid path given.")

    d = Directory.get_by_path(path)

    return jsonify({ 'id': d.id })


@auth.login_required
@directories.route("/create/", methods=["POST"])
def create_directory():
    if not g.current_user.admin:
        return unauthorized()


    name = request.json.get("name")
    path = request.json.get("path")

    parent = Directory.get_parent(path)

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


@auth.login_required
@directories.route("/rights/", methods=["POST"])
def get_directory_rights():
    if not g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")
    directory = Directory.get_by_path(path)
    return jsonify({'users': [ user.username for user in directory.users_with_rights ]})


@auth.login_required
@directories.route('/delete/', methods=["POST"])
def delete_directory():
    if g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")

    d = Directory.get_by_path(path)
    if not d:
        return bad_request("Directory does not exist")

    d.remove()
    return success("Directory with path: {0} successfully deleted".format(path))