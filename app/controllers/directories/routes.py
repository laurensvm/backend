from flask import jsonify, g, request

from . import directories
from ..authentication import auth
from ..statuscodes import unauthorized, success, bad_request, not_found
from ...exceptions import IOException
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
        amount = int(request.args.get("amount"))
    except ValueError as e:
        return bad_request("Amount cannot be converted to integer")
    except TypeError:
        amount = 30

    if not d:
        return not_found("Directory is not found")

    if not g.current_user in d.users_with_rights:
        return unauthorized()

    return jsonify({'files': [file.json() for file in d.files[:amount] ]})


@directories.route("/", methods=["GET"])
@auth.login_required
def get_children():
    try:
        amount = int(request.args.get("amount"))
    except ValueError as e:
        return bad_request("Could not convert amount to integer")
    except TypeError:
        amount = 30

    dirs = []
    directories = Directory.query.limit(amount).all()

    for dir in directories:
        if g.current_user in dir.users_with_rights:
            dirs.append(dir)

    return jsonify({ "directories": [ d.json() for d in dirs ] })


@directories.route("/root/", methods=["GET"])
@auth.login_required
def get_root():
    if not g.current_user.admin:
        return unauthorized()
    root = Directory.get_root_directory()
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

@directories.route("/<int:id>/rename/", methods=["POST"])
@auth.login_required
def rename_directory(id):
    if not g.current_user.admin:
        return unauthorized()

    name = request.json.get("name")

    if not name:
        return bad_request("No valid name given")

    d = Directory.get_by_id(id)

    if not d:
        return not_found("Directory is not found")

    try:
        d.rename(name)
    except IOException as e:
        return jsonify(e.json())

    return success("Directory id {dir} renamed to {name}".format(
        dir=d.id,
        name=d.name
    ))


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
        return bad_request("Directory with path '{0}' and name '{1}' already exists"
                           .format(parent.path, name))
    # Create directory
    d = Directory(
        parent_id=parent.id,
        name=name
    )
    d.users_with_rights.append(g.current_user)

    d.save()

    return success("Directory successfully created")


@directories.route("/<int:id>/rights/", methods=["GET"])
@auth.login_required
def get_directory_rights(id):
    if not g.current_user.admin:
        return unauthorized()

    directory = Directory.get_by_id(id)

    if not directory:
        return not_found("Directory with id {0} is not found".format(id))

    return jsonify({'users': [ user for user in directory.users_with_rights ]})


@directories.route('/delete/', methods=["POST"])
@auth.login_required
def delete_directory():
    if not g.current_user.admin:
        return unauthorized()

    path = request.json.get("path")

    d = Directory.get_by_path(path)
    if not d:
        return not_found("Directory could not be found")

    try:
        d.remove()
    except IOException as e:
        return jsonify(e.json())

    return success("Directory with path: {0} successfully deleted".format(path))

@directories.route("/<int:id>/delete/", methods=["GET"])
@auth.login_required
def delete_directory_by_id(id):
    if not g.current_user.admin:
        return unauthorized()

    d = Directory.get_by_id(id)
    if not d:
        return not_found("Directory could not be found")

    try:
        d.remove()
    except IOException as e:
        return jsonify(e.json())

    return success("Directory with id: {0} successfully deleted".format(id))
