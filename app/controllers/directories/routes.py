from flask import jsonify, g, request

from . import directories
from ..authentication import auth
from ..statuscodes import unauthorized, success, bad_request, not_found
from ...utils import join
from ...models import Directory

@directories.before_app_first_request
def create_root_directory():

    root = Directory.get_by_name("root")
    if not root:
        Directory.create_root()

    thumbnails = Directory.get_by_name("thumbnails")
    if not thumbnails:
        Directory.create_thumbnails()


@directories.route("/<int:id>/", methods=["GET"])
@auth.login_required
def get_directory_by_id(id):
    d = Directory.get_by_id(id)

    if not d:
        return not_found("Directory is not found")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify(d.json())

@directories.route("/<int:id>/files/", methods=["GET"])
@auth.login_required
def get_files_in_directory(id):
    d = Directory.get_by_id(id)

    try:
        amount = int(request.args.get("amount")) or 30
    except ValueError as e:
        return bad_request("Amount cannot be converted to integer")

    if not d:
        return not_found("Directory is not found")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [file.json() for file in d.files[:amount] ]})


@directories.route("/", methods=["GET", "POST"])
@auth.login_required
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


@directories.route("/root/", methods=["GET"])
@auth.login_required
def get_root():
    if not g.current_user.admin:
        return unauthorized()

    root = Directory.query.filter_by(name="root").first()
    return jsonify(root.json())


@directories.route("/id/", methods=["POST"])
@auth.login_required
def get_directory_id():
    path = request.json.get("path")

    if not path:
        return bad_request("No valid path given.")

    d = Directory.get_by_path(path)

    if not d:
        return not_found("Directory not found")

    return jsonify({ 'id': d.id })



@directories.route("/create/", methods=["POST"])
@auth.login_required
def create_directory():
    if not g.current_user.admin:
        return unauthorized()


    name = request.json.get("name")

    path = request.json.get("path")
    parent_id = request.json.get("parent_id")
    if path:
        parent = Directory.get_parent(path)
    elif parent_id:
        parent = Directory.query.filter_by(id=parent_id).first()

    if not parent:
        return bad_request("Directory with path does not exist")

    if parent.has_child_with_name(name):
        return bad_request("Directory with path {0} and name {1} already exists"
                           .format(path, name))
    # Create directory
    d = Directory(
        parent_id=parent.id,
        name=name
    )
    d.users_with_rights.append(g.current_user)

    d.save()

    return success("Directory successfully created")


@directories.route("/rights/", methods=["POST"])
@auth.login_required
def get_directory_rights():
    if not g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")
    directory = Directory.get_by_path(path)
    return jsonify({'users': [ user.username for user in directory.users_with_rights ]})


@directories.route('/delete/', methods=["POST"])
@auth.login_required
def delete_directory():
    if g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")

    d = Directory.get_by_path(path)
    if not d:
        return bad_request("Directory does not exist")

    d.remove()
    return success("Directory with path: {0} successfully deleted".format(path))
