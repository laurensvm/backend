from flask import jsonify, g, request, current_app

from . import files
from ..authentication import auth
from ..statuscodes import unauthorized, success, bad_request, not_found
from ... import utils
from ... import db
from ...models import Directory
from ...models import User

@files.before_app_first_request
def create_root_directory():
    root = Directory.query.filter_by(path="/").first()
    if not root:
        d = Directory(parent_id=None, name="root", path="/")
        admins = User.query.filter_by(admin=True)
        d.users_with_rights.extend(admins)

        db.session.add(d)
        db.session.commit()


@files.route("/", methods=["POST"])
@auth.login_required
def get_children():
    name = request.json.get("name")
    path = request.json.get("path")

    if name:
        directory = Directory.query.filter_by(name=name).first()
    elif path:
        directory = Directory.query.filter_by(path=path).first()
    else:
        return bad_request("No valid name or path given. Please use a path to combat ambiguity.")


    if directory:
        if g.current_user in directory.users_with_rights:
            return jsonify({ "children": [child.name for child in directory.children ] })
        return unauthorized()
    return not_found()

@files.route("/create/", methods=["POST"])
@auth.login_required
def create_directory():
    if g.current_user.admin:
        name = request.json.get("name")
        path = request.json.get("path")

        parent = Directory.query.filter_by(path=path).first()
        if parent:
            if not parent.has_child_with(name):
                # Create directory
                d = Directory(
                    parent_id=parent.id,
                    name=name,
                    path=utils.join(path, name))
                d.users_with_rights.append(g.current_user)

                db.session.add(d)
                db.session.commit()

                return success("Directory successfully created")

            return bad_request("Directory with path {0} and name {1} already exists"
                               .format(path, name))
        else:
            return bad_request("Directory with path does not exist")
    return unauthorized()

@files.route("/rights/", methods=["POST"])
@auth.login_required
def get_directory_rights():
    if g.current_user.admin:
        path = request.json.get("path")
        directory = Directory.query.filter_by(path=path).first()
        return jsonify({'users': [ user.username for user in directory.users_with_rights ]})
    return unauthorized()

@files.route('/delete/', methods=["POST"])
@auth.login_required
def delete_directory():
    if g.current_user.admin:
        path = request.json.get("path")

        d = Directory.query.filter_by(path=path).first()
        if d:
            d.remove()
            return success("Directory with path: {0} successfully deleted".format(path))
        return bad_request("Directory does not exist")
    return unauthorized()